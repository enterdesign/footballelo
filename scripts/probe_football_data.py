#!/usr/bin/env python3
"""One-off: what does the football-data.org free plan return for old seasons?"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

KEY = os.environ["FOOTBALL_DATA_KEY"]
BASE = "https://api.football-data.org/v4/competitions/{c}/matches?season={y}"


def get(url):
    for _ in range(4):
        req = urllib.request.Request(url, headers={"X-Auth-Token": KEY})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.status, json.load(r)
        except urllib.error.HTTPError as e:
            body = e.read().decode()[:200]
            if e.code == 429:
                time.sleep(20)
                continue
            return e.code, body
    return 429, "rate limited"


def probe(comp, years):
    for y in years:
        st, d = get(BASE.format(c=comp, y=y))
        if st == 200:
            ms = d["matches"]
            fin = [m for m in ms if m["status"] == "FINISHED"]
            stages = sorted({m["stage"] for m in ms})
            print(f"{comp} {y}: 200, {len(ms)} matches, {len(fin)} finished, stages={stages}", flush=True)
            if y == years[-1] and ms:
                print("  sample:", json.dumps(ms[0])[:900])
        else:
            print(f"{comp} {y}: {st} {d}", flush=True)
        time.sleep(7)


if __name__ == "__main__":
    probe("CL", [1992, 1999, 2004, 2010, 2011, 2014, 2018, 2022, 2024, 2025, 2026])
    probe("WC", [1930, 1954, 1974, 1990, 1998, 2006, 2010, 2014, 2018, 2022, 2026])
    st, d = get("https://api.football-data.org/v4/competitions")
    print("competitions:", st, [c["code"] for c in d["competitions"]] if st == 200 else d)
