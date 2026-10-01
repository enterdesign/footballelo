#!/usr/bin/env python3
"""Europa League and Conference League from English Wikipedia into data/matches/{el,conf}.json.

usage: import_uefa.py [--init-teams] [--only el|conf] [--report FILE]
  (default)      refetch every season
  --init-teams   create data/teams_{el,conf}.json entries for clubs not yet known (first import only;
                 afterwards unknown names stop the daily build instead)
"""
import argparse
import json
import re
import unicodedata
from collections import Counter
from datetime import date
from pathlib import Path

from common import DATA, alias_map
import uefa_wikipedia as uw

CODES = {"Albania": "ALB", "Andorra": "AND", "Armenia": "ARM", "Austria": "AUT", "Azerbaijan": "AZE", "Belarus": "BLR",
         "Belgium": "BEL", "Bosnia and Herzegovina": "BIH", "Bulgaria": "BUL", "Croatia": "CRO", "Cyprus": "CYP",
         "Czechia": "CZE", "Denmark": "DEN", "England": "ENG", "Estonia": "EST", "Faroe Islands": "FRO",
         "Finland": "FIN", "France": "FRA", "Georgia": "GEO", "Germany": "GER", "Gibraltar": "GIB", "Greece": "GRE",
         "Hungary": "HUN", "Iceland": "ISL", "Israel": "ISR", "Italy": "ITA", "Kazakhstan": "KAZ", "Kosovo": "KVX",
         "Latvia": "LVA", "Liechtenstein": "LIE", "Lithuania": "LTU", "Luxembourg": "LUX", "Malta": "MLT",
         "Moldova": "MDA", "Montenegro": "MNE", "Netherlands": "NED", "North Macedonia": "MKD",
         "Northern Ireland": "NIR", "Norway": "NOR", "Poland": "POL", "Portugal": "POR", "Republic of Ireland": "IRL",
         "Romania": "ROU", "Russia": "RUS", "San Marino": "SMR", "Scotland": "SCO", "Serbia": "SRB", "Slovakia": "SVK",
         "Slovenia": "SVN", "Spain": "ESP", "Sweden": "SWE", "Switzerland": "SUI", "Turkey": "TUR", "Ukraine": "UKR",
         "Wales": "WAL"}
COUNTRY = {"the Czech Republic": "Czechia", "Czech Republic": "Czechia", "Ireland": "Republic of Ireland",
           "the Netherlands": "Netherlands", "the Faroe Islands": "Faroe Islands"}
NOISE = re.compile(r"\b(fc|f c|afc|sc|cf|ac|as|sk|fk|nk|ks|bk|if|sv|us|ssc|rcd|ud|cd|club|football|futbol|de|calcio)\b")


def nk(s):
    """Loose key: lower case, accents/punctuation/club-form words removed."""
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"\([^)]*\)", " ", s)
    s = NOISE.sub(" ", re.sub(r"[^a-z0-9 ]", " ", s))
    return re.sub(r"\s+", "", s)


def fetch_all(comp, first=None):
    matches, info = [], {}
    today = date.today()
    last = today.year if today.month >= 7 else today.year - 1
    for year in range(first or uw.FIRST[comp], last + 1):
        ms, inf = uw.fetch_season(comp, year)
        print(f"{comp} {uw.label(year)}: {len(ms)} matches")
        matches += ms
        for k, v in inf.items():
            d = info.setdefault(k, {"shown": Counter(), "country": Counter()})
            d["shown"].update(v["shown"])
            d["country"].update(v["country"])
    matches.sort(key=lambda m: (m["season"], m["date"]))
    return matches, info


def init_teams(comp, matches, info, existing):
    """Add a team entry for every article title not covered by `existing`. Returns (teams, report lines)."""
    teams = dict(existing)
    amap = alias_map(teams)
    ucl = json.loads((DATA / "teams_ucl.json").read_text(encoding="utf-8"))
    ucl_by_key = {}
    for canon, e in ucl.items():
        for n in [canon, *e.get("aliases", [])]:
            ucl_by_key.setdefault(nk(n), canon)
    new = sorted({t for m in matches for t in (m["teamA"], m["teamB"])} - set(amap))
    final = uw.resolve_redirects(new)
    clusters = {}
    for t in new:
        clusters.setdefault(final.get(t, t), []).append(t)
    report = []
    for res, members in sorted(clusters.items()):
        shown, country = Counter(), Counter()
        for t in members + ([res] if res not in members else []):
            if t in info:
                shown.update(info[t]["shown"])
                country.update(info[t]["country"])
        name = shown.most_common(1)[0][0] if shown else res
        c = COUNTRY.get(country.most_common(1)[0][0], country.most_common(1)[0][0]) if country else ""
        hit = next((ucl_by_key[k] for k in (nk(name), nk(res)) if k in ucl_by_key), None)
        entry = {"aliases": sorted({*members, res} - {name})}
        if hit and (not c or ucl[hit].get("country") == c):
            entry["code"], entry["country"] = ucl[hit]["code"], ucl[hit]["country"]
            if ucl[hit].get("logo"):
                entry["logo"] = ucl[hit]["logo"]
            name = hit if hit not in teams else name
            entry["aliases"] = sorted({*members, res, *([hit] if hit != name else [])} - {name})
        else:
            entry["country"], entry["code"] = c, CODES.get(c, c[:3].upper())
            if not c:
                report.append(f"no country: {name} ({res})")
        if name in teams or name in amap:                       # same display name, different club
            name = res
        teams[name] = entry
        amap.update({a: name for a in [name, *entry["aliases"]]})
    return teams, report


def dump_teams(path, teams):
    lines = [json.dumps(k, ensure_ascii=False) + ":" + json.dumps(v, ensure_ascii=False, separators=(",", ":"))
             for k, v in sorted(teams.items())]
    Path(path).write_text("{\n" + ",\n".join(lines) + "\n}\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--init-teams", action="store_true")
    ap.add_argument("--only", choices=["el", "conf"])
    ap.add_argument("--report")
    args = ap.parse_args()
    report = []
    for comp in ([args.only] if args.only else ["el", "conf"]):
        matches, info = fetch_all(comp)
        (DATA / f"matches/{comp}.json").write_text(json.dumps(matches, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        report.append(f"{comp}: {len(matches)} matches, {len({t for m in matches for t in (m['teamA'], m['teamB'])})} article titles")
        if args.init_teams:
            path = DATA / f"teams_{comp}.json"
            existing = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
            teams, rep = init_teams(comp, matches, info, existing)
            dump_teams(path, teams)
            report += [f"{comp}: {len(teams)} teams"] + rep
    text = "\n".join(report)
    print(text)
    if args.report:
        Path(args.report).write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
