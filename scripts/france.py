"""French top flight (Division 1 1932/33-2001/02, Ligue 1 2002/03-).

Sources
  * engsoccerdata (france.csv, tier 1)  -> seasons before 2014/15 (frozen archive)
  * footballcsv/france                  -> fills what the archive lacks: all of 1937/38 and 1994/95, and the
                                           2006/07 match Nantes-Toulouse (see FILL)
  * openfootball/france                 -> 2014/15 onwards (refreshed daily)
All matches are rated with the single phase "league".
"""
import csv
from pathlib import Path

import england

FIRST_OF = "2014/15"
# (season, whole): whole seasons missing from engsoccerdata are taken from footballcsv in full; for the others only
# the listed (home, away) pairs are added
FILL = {"1937/38": None, "1994/95": None, "2006/07": [("FC Nantes", "Toulouse FC")]}


def parse_openfootball(root, first=FIRST_OF):
    out = []
    for f in sorted(Path(root).glob("[12][0-9][0-9][0-9]-[0-9][0-9]_fr1.txt")):
        season = england.season_label(f.name)
        if season >= first:
            out.extend(england.parse_file(f, season))
    return out


def parse_footballcsv(root, season):
    """Matches of one season from a footballcsv/france checkout (<season dir>/fr.csv, 'Date,Team 1,FT,Team 2')."""
    d = f"{season[:4]}-{season[5:]}"
    out = []
    with open(Path(root) / d / "fr.csv", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            a, b = r["FT"].split("-")
            out.append({"season": season, "phase": "league", "teamA": r["Team 1"], "goalsA": int(a),
                        "teamB": r["Team 2"], "goalsB": int(b), "date": r["Date"]})
    return out


def parse_engsoccerdata(csv_path, before=FIRST_OF):
    rows = []
    with open(csv_path, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if r["tier"] != "1":
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
