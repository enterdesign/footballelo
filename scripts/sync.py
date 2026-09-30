#!/usr/bin/env python3
"""Refresh data/matches/*.json from openfootball.

usage: sync.py [--worldcup DIR] [--ucl DIR]   (default: shallow-clone both repos)
World Cup is replaced wholesale. For the Champions League seasons from
2011/12 on are replaced; older seasons (not covered by the source) are kept.
"""
import argparse
import json
import os
import subprocess
import tempfile
from datetime import date
from pathlib import Path

from common import DATA
import footballdata
import openfootball

UCL_FIRST = "2011/12"


def clone(name, dest):
    subprocess.run(["git", "clone", "-q", "--depth", "1",
                    f"https://github.com/openfootball/{name}", str(dest)], check=True)
    return dest


def dump(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def with_current_season(old, ucl):
    """The running Champions League season comes from football-data.org (live, needs
    env FOOTBALL_DATA_KEY); openfootball is often weeks behind. Its free plan only
    covers the last few seasons, so older ones stay as imported from openfootball."""
    today = date.today()
    year = today.year if today.month >= 7 else today.year - 1
    season = f"{year}/{str(year + 1)[2:]}"
    key = os.environ.get("FOOTBALL_DATA_KEY")
    if not key:
        return ucl
    try:
        fresh = footballdata.convert(footballdata.fetch(year, key), season)
    except Exception as e:                      # keep what we already have
        print(f"football-data.org failed ({e}); keeping existing {season} matches")
        if not any(m["season"] == season for m in ucl):
            ucl += [m for m in old if m["season"] == season]
        return ucl
    print(f"{season}: {len(fresh)} matches from football-data.org")
    return [m for m in ucl if m["season"] != season] + fresh


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--worldcup")
    ap.add_argument("--ucl")
    args = ap.parse_args()
    with tempfile.TemporaryDirectory() as tmp:
        wc_dir = args.worldcup or clone("worldcup", Path(tmp) / "worldcup")
        ucl_dir = args.ucl or clone("champions-league", Path(tmp) / "champions-league")
        wc = openfootball.parse_worldcup(wc_dir)
        ucl_new = openfootball.parse_ucl(ucl_dir, UCL_FIRST.replace("/", "-"))
    for m in ucl_new:
        m.pop("codeA", None)
        m.pop("codeB", None)
    old = json.loads((DATA / "matches/ucl.json").read_text(encoding="utf-8"))
    ucl = [m for m in old if m["season"] < UCL_FIRST] + ucl_new
    ucl = with_current_season(old, ucl)
    dump(DATA / "matches/wc.json", wc)
    dump(DATA / "matches/ucl.json", ucl)
    print(f"world cup: {len(wc)} matches, champions league: {len(ucl)} matches")


if __name__ == "__main__":
    main()
