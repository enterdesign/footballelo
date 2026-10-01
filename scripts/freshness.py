#!/usr/bin/env python3
"""Alarm for silent source failures: a running competition whose number of matches has not changed for weeks.

Reads data/sync.json ("feeds": {competition: {"n", "changed"}}, written by sync.py). Exit status 3 and a
readable report when something looks stale, 0 otherwise. Only months in which the competition certainly plays
every week or two are checked, so summer and winter breaks never raise a false alarm.

usage: freshness.py [--today YYYY-MM-DD]
"""
import argparse
import sys
from datetime import date

from common import DATA, load

MAX_DAYS = 21
# competition -> months in which a gap of three weeks means something is wrong
WINDOWS = {"ucl": {10, 11, 3, 4, 5}, "el": {10, 11, 3, 4, 5}, "conf": {10, 11, 3, 4, 5},
           "pl": {9, 10, 11, 12, 1, 2, 3, 4, 5}, "ekstraklasa": {9, 10, 11, 3, 4, 5}}
NL_MONTHS = {10, 11}            # league phase of the Nations League, in the years with an edition (even years)
NAMES = {"ucl": "Champions League", "el": "Europa League", "conf": "Conference League", "pl": "Premier League",
         "ekstraklasa": "Ekstraklasa", "nl": "Nations League"}


def stale(feeds, today):
    """[(competition, days since the number of matches last changed)]."""
    out = []
    for comp, f in feeds.items():
        months = WINDOWS.get(comp)
        if comp == "nl" and today.year % 2 == 0:
            months = NL_MONTHS
        if not months or today.month not in months:
            continue
        days = (today - date.fromisoformat(f["changed"])).days
        if days > MAX_DAYS:
            out.append((comp, days))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--today")
    args = ap.parse_args()
    today = date.fromisoformat(args.today) if args.today else date.today()
    sync = DATA / "sync.json"
    feeds = load(sync).get("feeds", {}) if sync.exists() else {}
    bad = stale(feeds, today)
    for comp, days in bad:
        print(f"{NAMES.get(comp, comp)}: no new matches for {days} days (last change {feeds[comp]['changed']})")
    if not bad:
        print("all running competitions delivered matches recently")
    sys.exit(3 if bad else 0)


if __name__ == "__main__":
    main()
