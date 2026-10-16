"""Spanish top flight (Primera División / La Liga 1928/29-).

Sources
  * engsoccerdata (spain.csv, tier 1)   -> seasons before 2012/13 (frozen archive)
  * openfootball/espana                 -> 2012/13 onwards (refreshed daily)
All matches are rated with the single phase "league". The 1986/87 promotion/relegation group stage
("phase2" in engsoccerdata, played with second-division clubs) is not rated.
"""
import csv
from pathlib import Path

import england

FIRST_OF = "2012/13"


def parse_openfootball(root, first=FIRST_OF):
    out = []
    for f in sorted(Path(root).glob("[12][0-9][0-9][0-9]-[0-9][0-9]/1-liga.txt")):
        season = england.season_label(f.parent.name)
        if season >= first:
            out.extend(england.parse_file(f, season))
    return out


def parse_engsoccerdata(csv_path, before=FIRST_OF):
    rows = []
    with open(csv_path, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if r["tier"] != "1" or r["round"] != "league":
                continue
            y = int(r["Season"])
            season = f"{y}/{str(y + 1)[2:]}"
            if season >= before:
                continue
            rows.append((season, r["Date"], {"season": season, "phase": "league", "teamA": r["home"],
                                             "goalsA": int(r["hgoal"]), "teamB": r["visitor"],
                                             "goalsB": int(r["vgoal"])}))
    rows.sort(key=lambda x: (x[0], x[1]))
    return [r[2] for r in rows]
