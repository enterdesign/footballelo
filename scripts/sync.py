#!/usr/bin/env python3
"""Refresh data/matches/*.json.

usage: sync.py [--worldcup DIR] [--ucl DIR] [--england DIR]   (default: shallow-clone the openfootball repos)

* World Cup: replaced wholesale from openfootball.
* Champions League: seasons from 2011/12 replaced from openfootball, older ones kept.
* Premier League: seasons from 1992/93 replaced from openfootball; the First Division
  archive (1888/89-1991/92, from engsoccerdata) is kept.
* Running season of the Champions League and Premier League: football-data.org when
  FOOTBALL_DATA_KEY is set (it is live; openfootball is often weeks behind).
"""
import argparse
import json
import os
import subprocess
import tempfile
from datetime import date
from pathlib import Path

from common import DATA
import england
import footballdata
import openfootball

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

    dump(DATA / "matches/wc.json", wc)
    dump(DATA / "matches/ucl.json", ucl)
    dump(DATA / "matches/pl.json", pl)
    print(f"world cup: {len(wc)}, champions league: {len(ucl)}, premier league: {len(pl)} matches")


if __name__ == "__main__":
    main()
