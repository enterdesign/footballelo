#!/usr/bin/env python3
"""Import the Polish top flight from English Wikipedia into data/matches/ekstraklasa.json.

usage: import_ekstraklasa.py [--recent N] [--init-teams] [--report FILE]
  --recent N     only (re)fetch the last N seasons (default: all seasons)
  --init-teams   create data/teams_ekstraklasa.json entries for names not yet known
                 (first import only; afterwards unknown names stop the weekly build instead)
"""
import argparse
import json
import time
from collections import Counter
from pathlib import Path

from common import DATA, alias_map
import wikipedia_pl as wp

MATCHES = DATA / "matches/ekstraklasa.json"
TEAMS = DATA / "teams_ekstraklasa.json"


def load(path, default):
    return json.loads(Path(path).read_text(encoding="utf-8")) if Path(path).exists() else default


def import_seasons(labels, titles, delay=1.0):
    """[(season, matches, shown_names)] for the given season labels."""
    out = []
    for label in labels:
        wt = wp.fetch_season(titles[label])
        ms = wp.parse_season(wt, label)
        shown = {}
        for b in wp.blocks(wt):
            for r in wp.parse_block(b):
                shown.setdefault(r["teamA"], set()).add(r["shownA"])
                shown.setdefault(r["teamB"], set()).add(r["shownB"])
        out.append((label, ms, shown))
        time.sleep(delay)
    return out


def describe(label, ms):
    teams = {t for m in ms for t in (m["teamA"], m["teamB"])}
    n = len(teams)
    pairs = Counter(frozenset((m["teamA"], m["teamB"])) for m in ms)
    full = n * (n - 1)
    flag = "ok" if len(ms) == full else ("split?" if len(ms) > full else "CHECK")
    return f"{label:8} teams={n:2} matches={len(ms):4} expected(2x round robin)={full:4} {flag}" \
           f"  max games per pair={max(pairs.values()) if pairs else 0}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--recent", type=int)
    ap.add_argument("--init-teams", action="store_true")
    ap.add_argument("--report")
    args = ap.parse_args()

    titles = wp.season_titles()
    labels = list(titles)
    print(f"{len(labels)} season articles: {labels[0]} .. {labels[-1]}")
    fetch = labels[-args.recent:] if args.recent else labels
    result = import_seasons(fetch, titles)

    old = load(MATCHES, [])
    fresh = {label for label, _, _ in result}
    matches = [m for m in old if m["season"] not in fresh]
    for _, ms, _ in result:
        matches.extend(ms)
    matches.sort(key=lambda m: m["season"])                       # stable: article order inside a season
    MATCHES.write_text(json.dumps(matches, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    lines = [describe(label, ms) for label, ms, _ in result]
    empty = [label for label, ms, _ in result if not ms]
    lines.append(f"total {len(matches)} matches; seasons without a parsable results table: {empty or 'none'}")
    lines.append("seasons missing from the category (no article): " + ", ".join(
        y for y in (str(x) for x in range(1927, 2027)) if y not in titles and not any(l.startswith(y + "/") or l.endswith("/" + y[2:]) for l in titles)))

    if args.init_teams:
        teams = load(TEAMS, {})
        shown_all = {}
        for _, _, shown in result:
            for t, s in shown.items():
                shown_all.setdefault(t, set()).update(s)
        known = alias_map(teams)
        for t in sorted(shown_all):
            canon = known.get(t, t)                       # names merged by hand keep pointing at their club
            entry = teams.setdefault(canon, {"country": "Poland", "aliases": []})
            new = (shown_all[t] | {t}) - {canon}
            new = {a for a in new if known.setdefault(a, canon) == canon}   # first club to claim a name keeps it
            known.setdefault(canon, canon)
            entry["aliases"] = sorted(set(entry["aliases"]) | new)
        TEAMS.write_text(json.dumps(dict(sorted(teams.items())), ensure_ascii=False, indent=1), encoding="utf-8")
        lines.append(f"teams file: {len(teams)} clubs")
    text = "\n".join(lines)
    print(text)
    if args.report:
        Path(args.report).write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
