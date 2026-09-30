#!/usr/bin/env python3
"""One-off: dump team names/crests that football-data.org returns (free plan)."""
import json
import os
import time
import urllib.error
import urllib.request

KEY = os.environ["FOOTBALL_DATA_KEY"]


def get(url):
    for _ in range(4):
        req = urllib.request.Request(url, headers={"X-Auth-Token": KEY})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(20)
                continue
            print("ERR", url, e.code)
            return {}
    return {}


seen = {}
for comp, year in (("CL", 2026), ("CL", 2025), ("CL", 2024), ("WC", 2026)):
    d = get(f"https://api.football-data.org/v4/competitions/{comp}/teams?season={year}")
    for t in d.get("teams", []):
        seen.setdefault(t["id"], (comp, t))
    time.sleep(7)
for i, (comp, t) in sorted(seen.items(), key=lambda kv: (kv[1][0], kv[1][1]["name"])):
    print("|".join(str(x) for x in (comp, i, t["name"], t.get("shortName"), t.get("tla"),
                                    (t.get("area") or {}).get("name"), t.get("crest"))))
print("TOTAL", len(seen))
