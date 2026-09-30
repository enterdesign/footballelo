"""English top flight (First Division 1888/89-1991/92, Premier League 1992/93-).

Sources
  * engsoccerdata (england.csv, tier 1)  -> seasons before 1992/93 (frozen archive)
  * openfootball/england                 -> 1992/93 onwards (refreshed weekly)
All matches are rated with the single phase "league".
"""
import csv
import re
from pathlib import Path

FIRST_PL = "1992/93"

SCORE = re.compile(r"(?<![\w(])(\d{1,2})-(\d{1,2})(?![\w)])")
TIME = re.compile(r"^\s*\d{1,2}:\d{2}\s+")


def season_label(dirname):
    return dirname[:4] + "/" + dirname[5:7]


def parse_line(line):
    """One openfootball fixture line -> (teamA, goalsA, teamB, goalsB) or None."""
    if not line.strip() or line.lstrip().startswith(("=", "#", "▪")):
        return None
    line = TIME.sub("", line.rstrip())
    if " v " in line:                                   # "Liverpool  v AFC Bournemouth  4-2 (1-0)"
        left, right = re.split(r"\s+v\s+", line.strip(), maxsplit=1)
        m = SCORE.search(right)
        if not m:
            return None
        return left.strip(), int(m.group(1)), right[: m.start()].strip(), int(m.group(2))
    m = SCORE.search(line)                              # archive: "Bolton Wanderers FC   3-6  Derby County FC"
    if not m:
        return None
    a, b = line[: m.start()].strip(), re.sub(r"^\(\d{1,2}-\d{1,2}\)\s*|\s*\(\d{1,2}-\d{1,2}\)\s*$", "", line[m.end():].strip()).strip()
    if not a or not b or re.match(r"^[A-Z][a-z]{2}\s", a) and len(a) < 12:
        return None
    return a, int(m.group(1)), b, int(m.group(2))


def parse_file(path, season):
    out = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        r = parse_line(line)
        if r:
            out.append({"season": season, "phase": "league", "teamA": r[0], "goalsA": r[1],
                        "teamB": r[2], "goalsB": r[3]})
    return out


def parse_openfootball(root, first=FIRST_PL):
    """All top-flight seasons found under openfootball/england (season dirs + archive/)."""
    root = Path(root)
    found = {}
    for f in list(root.glob("[12][0-9][0-9][0-9]-[0-9][0-9]/1-*.txt")) + \
            list(root.glob("archive/*/[12][0-9][0-9][0-9]-[0-9][0-9]/1-*.txt")):
        if f.name.endswith("-full.txt"):
            continue
        found[f.parent.name] = f
    out = []
    for d in sorted(found):
        season = season_label(d)
        if season >= first:
            out.extend(parse_file(found[d], season))
    return out


def parse_engsoccerdata(csv_path, before=FIRST_PL):
    """Tier-1 matches of seasons earlier than `before`, in date order."""
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
