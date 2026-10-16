"""Italian top flight (Serie A 1929/30-).

Sources
  * engsoccerdata (italy.csv, tier 1)   -> seasons before 2013/14 (frozen archive)
  * openfootball/italy                  -> 2013/14 onwards (refreshed daily)
All matches are rated with the single phase "league". Not included: 1943-45 (no league, war) and 1945/46
(played in two regional groups and incomplete in the archive). 40 of the 420 matches of 1947/48 are missing from
the archive and from every other free source.
"""
import csv
import re
from pathlib import Path

import england

FIRST_OF = "2013/14"
SKIP = {"1945/46"}


def parse_openfootball(root, first=FIRST_OF):
    out = []
    for f in sorted(Path(root).glob("[12][0-9][0-9][0-9]-[0-9][0-9]/1-seriea.txt")):
        season = england.season_label(f.parent.name)
        if season >= first:
            out.extend(england.parse_file(f, season))
    for m in out:                                         # "AS Roma   [awarded]": a match decided at the table
        m["teamA"], m["teamB"] = (re.sub(r"\s*\[awarded\]", "", t).strip() for t in (m["teamA"], m["teamB"]))
    return out


def parse_engsoccerdata(csv_path, before=FIRST_OF):
    rows = []
    with open(csv_path, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if r["tier"] != "1":
                continue
            y = int(r["Season"])
            if r["Date"] < f"{y}-08-15":                  # play-off of the previous season, filed under the next one
                y -= 1
            season = f"{y}/{str(y + 1)[2:]}"
            if season >= before or season in SKIP:
                continue
            rows.append((season, r["Date"], {"season": season, "phase": "league", "teamA": r["home"],
                                             "goalsA": int(r["hgoal"]), "teamB": r["visitor"],
                                             "goalsB": int(r["vgoal"])}))
    rows.sort(key=lambda x: (x[0], x[1]))
    return [r[2] for r in rows]
