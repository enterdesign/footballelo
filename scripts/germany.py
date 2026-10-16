"""German top flight (Bundesliga 1963/64-).

Sources
  * engsoccerdata (germany.csv, tier 1)   -> seasons before 2010/11 (frozen archive)
  * openfootball/deutschland              -> 2010/11 onwards (refreshed daily)
All matches are rated with the single phase "league". Names are mapped to canonical clubs through
data/teams_bundesliga.json (the two sources spell clubs differently).
"""
import csv
from pathlib import Path

import england

FIRST_OF = "2010/11"


def parse_openfootball(root, first=FIRST_OF):
    """All Bundesliga seasons found under openfootball/deutschland (<season>/1-bundesliga.txt)."""
    out = []
    for f in sorted(Path(root).glob("[12][0-9][0-9][0-9]-[0-9][0-9]/1-bundesliga.txt")):
        season = england.season_label(f.parent.name)
        if season >= first:
            out.extend(england.parse_file(f, season))
    return out


def parse_engsoccerdata(csv_path, before=FIRST_OF):
    """Tier-1 matches of seasons earlier than `before`, in date order."""
    return england.parse_engsoccerdata(csv_path, before)
