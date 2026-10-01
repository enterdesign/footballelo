#!/usr/bin/env python3
"""Refresh data/matches/*.json.

usage: sync.py [--worldcup DIR] [--ucl DIR] [--england DIR]   (default: shallow-clone the openfootball repos)

* World Cup: replaced wholesale from openfootball.
* Champions League: seasons from 2011/12 replaced from openfootball, older ones kept.
* Premier League: seasons from 1992/93 replaced from openfootball; the First Division
  archive (1888/89-1991/92, from engsoccerdata) is kept.
* Nations League: replaced wholesale from the open international_results dataset (see nationsleague.py).
* Running season of the Champions League and Premier League: football-data.org when
  FOOTBALL_DATA_KEY is set (it is live; openfootball is often weeks behind).
"""
import argparse
import json
import os
import subprocess
import tempfile
from datetime import date, datetime, timezone
from pathlib import Path

from common import DATA, alias_map
import england
import footballdata
import import_ekstraklasa
import nationsleague
import nl_wikipedia
import openfootball
import wikipedia_pl

UCL_FIRST = "2011/12"


def clone(name, dest):
    subprocess.run(["git", "clone", "-q", "--depth", "1",
                    f"https://github.com/openfootball/{name}", str(dest)], check=True)
    return dest


def dump(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def load_old(name):
    return json.loads((DATA / f"matches/{name}.json").read_text(encoding="utf-8"))


def with_current_season(old, matches, comp, stages):
    """Replace the running season by football-data.org's live data (needs FOOTBALL_DATA_KEY).
    Its free plan only covers the last few seasons, so older ones are left alone."""
    today = date.today()
    year = today.year if today.month >= 7 else today.year - 1
    season = f"{year}/{str(year + 1)[2:]}"
    key = os.environ.get("FOOTBALL_DATA_KEY")
    if not key:                                 # nothing newer available: keep the running season
        if not any(m["season"] == season for m in matches):
            matches += [m for m in old if m["season"] == season]
        return matches
    try:
        fresh = footballdata.convert(footballdata.fetch(year, key, comp), season, stages)
    except Exception as e:                      # keep what we already have
        print(f"football-data.org {comp} failed ({e}); keeping existing {season} matches")
        if not any(m["season"] == season for m in matches):
            matches += [m for m in old if m["season"] == season]
        return matches
    print(f"{comp} {season}: {len(fresh)} matches from football-data.org")
    return [m for m in matches if m["season"] != season] + fresh


def refresh_ekstraklasa(recent=2):
    """Latest seasons of the Polish league from Wikipedia. A season is only replaced when the fresh
    copy has at least as many matches as the stored one (a half-edited article never shrinks it)."""
    old = load_old("ekstraklasa")
    try:
        titles = wikipedia_pl.season_titles()
        result = import_ekstraklasa.import_seasons(list(titles)[-recent:], titles)
    except Exception as e:
        print(f"Wikipedia (Ekstraklasa) failed ({e}); keeping stored data")
        return old
    matches = list(old)
    for label, ms, _ in result:
        stored = [m for m in old if m["season"] == label]
        if len(ms) >= len(stored):
            matches = [m for m in matches if m["season"] != label] + ms
        else:
            print(f"Ekstraklasa {label}: fresh copy has fewer matches ({len(ms)} < {len(stored)}); kept stored")
    matches.sort(key=lambda m: m["season"])
    return matches


def refresh_nl():
    """Nations League: the open dataset (history, shoot-out winners) plus the running edition from Wikipedia,
    which is days ahead of the dataset. A wiki match is dropped as soon as the dataset has it
    (same teams, dates within 20 days). Stored data is kept when a download fails or looks truncated."""
    old = load_old("nl")
    try:
        fresh = nationsleague.parse(nationsleague.fetch(nationsleague.RESULTS), nationsleague.fetch(nationsleague.SHOOTOUTS))
    except Exception as e:
        print(f"international_results failed ({e}); keeping stored Nations League data")
        return old
    if len(fresh) < len(old):
        print(f"Nations League: fresh copy has fewer matches ({len(fresh)} < {len(old)}); kept stored")
        return old
    amap = alias_map(json.loads((DATA / "teams_nl.json").read_text(encoding="utf-8")))
    canon = lambda t: amap.get(t, t)
    try:
        wiki = nl_wikipedia.fetch_running()
    except Exception as e:
        print(f"Wikipedia (Nations League) failed ({e}); using the dataset only")
        wiki = []
    have = {}
    for m in fresh:
        have.setdefault((canon(m["teamA"]), canon(m["teamB"])), []).append(m["date"])
    extra = [m for m in wiki if not any(abs(nationsleague.days(m["date"], d)) <= 20
                                        for d in have.get((canon(m["teamA"]), canon(m["teamB"])), []))]
    print(f"Nations League: {len(fresh)} from the dataset, {len(extra)} more from Wikipedia")
    return sorted(fresh + extra, key=lambda m: m["date"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--worldcup")
    ap.add_argument("--ucl")
    ap.add_argument("--england")
    args = ap.parse_args()
    with tempfile.TemporaryDirectory() as tmp:
        wc_dir = args.worldcup or clone("worldcup", Path(tmp) / "worldcup")
        ucl_dir = args.ucl or clone("champions-league", Path(tmp) / "champions-league")
        eng_dir = args.england or clone("england", Path(tmp) / "england")
        wc = openfootball.parse_worldcup(wc_dir)
        ucl_new = openfootball.parse_ucl(ucl_dir, UCL_FIRST.replace("/", "-"))
        pl_new = england.parse_openfootball(eng_dir)
    for m in ucl_new:
        m.pop("codeA", None)
        m.pop("codeB", None)

    old = load_old("ucl")
    ucl = [m for m in old if m["season"] < UCL_FIRST] + ucl_new
    ucl = with_current_season(old, ucl, "CL", footballdata.STAGES)

    old = load_old("pl")
    pl = [m for m in old if m["season"] < england.FIRST_PL] + pl_new
    pl = with_current_season(old, pl, "PL", footballdata.PL_STAGES)

    ekstraklasa = refresh_ekstraklasa()
    nl = refresh_nl()
    dump(DATA / "matches/nl.json", nl)
    dump(DATA / "matches/ekstraklasa.json", ekstraklasa)
    dump(DATA / "matches/wc.json", wc)
    dump(DATA / "matches/ucl.json", ucl)
    dump(DATA / "matches/pl.json", pl)
    # heartbeat: shown on the home page, and the daily commit keeps the schedule alive
    dump(DATA / "sync.json", {"synced": datetime.now(timezone.utc).isoformat(timespec="minutes")})
    print(f"world cup: {len(wc)}, champions league: {len(ucl)}, premier league: {len(pl)}, "
          f"ekstraklasa: {len(ekstraklasa)}, nations league: {len(nl)} matches")


if __name__ == "__main__":
    main()
