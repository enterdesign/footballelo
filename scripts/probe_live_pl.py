#!/usr/bin/env python3
"""One-off: which free sources have CURRENT Polish league results?"""
import csv
import io
import json
import urllib.request

UA = {"User-Agent": "footballelo/1.0 (personal ELO project)"}


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return r.read().decode("utf-8-sig", "replace")


try:
    txt = get("https://www.football-data.co.uk/new/POL.csv")
    rows = list(csv.DictReader(io.StringIO(txt)))
    print("football-data.co.uk POL.csv rows:", len(rows), "columns:", list(rows[0].keys())[:14])
    seasons = {}
    for r in rows:
        seasons[r.get("Season")] = seasons.get(r.get("Season"), 0) + 1
    print("rows per season:", dict(list(seasons.items())[-6:]), "first:", list(seasons.items())[:2])
    for r in rows[-6:]:
        print("  ", {k: r[k] for k in ("Season", "Date", "Home", "Away", "HG", "AG", "Res") if k in r})
except Exception as e:
    print("football-data.co.uk ERR", e)

for season in ("2026-2027", "2025-2026"):
    try:
        d = json.loads(get(f"https://www.thesportsdb.com/api/v1/json/3/eventsseason.php?id=4422&s={season}"))
        ev = d.get("events") or []
        played = [e for e in ev if e.get("intHomeScore") not in (None, "")]
        print(f"TheSportsDB Ekstraklasa {season}: {len(ev)} events, {len(played)} with a score")
        for e in played[-3:]:
            print("  ", e.get("dateEvent"), e.get("strHomeTeam"), e.get("intHomeScore"), "-", e.get("intAwayScore"), e.get("strAwayTeam"))
    except Exception as e:
        print("TheSportsDB ERR", season, e)
