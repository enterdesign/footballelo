#!/usr/bin/env python3
"""Build site/data/{ucl,wc}.json (ranking + per-match history) from data/.

Exits with status 2 (and a readable report) if a team name has no entry in
data/teams_*.json, so new names are never guessed.
"""
import json
import sys
from datetime import datetime, timezone

from common import DATA, ROOT, alias_map, load, unknown_names
import elo

COMPS = {
    "ucl": {"teams": "teams_ucl.json", "period": "season", "title": "UEFA Champions League"},
    "wc": {"teams": "teams_wc.json", "period": "year", "title": "FIFA World Cup"},
}


def apply_overrides(matches, ov, period):
    def same(m, r):
        return all(m.get(k) == v for k, v in r.items())
    for r in ov.get("remove", []):
        n = len(matches)
        matches = [m for m in matches if not same(m, r)]
        if len(matches) == n:
            print(f"  warning: override 'remove' matched nothing: {r}", file=sys.stderr)
    return matches + ov.get("add", [])


def build(key):
    cfg = COMPS[key]
    teams = load(DATA / cfg["teams"])
    phases = load(DATA / "phases.json")[key]
    amap = alias_map(teams)
    period = cfg["period"]
    matches = load(DATA / "matches" / f"{key}.json")
    matches = apply_overrides(matches, load(DATA / "overrides.json").get(key, {}), period)
    bad = unknown_names(matches, amap)
    if bad:
        return None, bad
    matches.sort(key=lambda m: str(m[period]))          # stable: file order inside a period
    for m in matches:
        m["teamA"], m["teamB"] = amap[m["teamA"]], amap[m["teamB"]]
        if m["phase"] not in phases:
            raise SystemExit(f"{key}: unknown phase {m['phase']!r} in {m}")
    ratings, count, hist = elo.run(matches, phases, seed=teams)
    order = sorted(ratings, key=lambda t: (-ratings[t], t))
    idx = {t: i for i, t in enumerate(order)}
    out = {
        "title": cfg["title"],
        "phases": phases,
        "teams": [{"name": t, **{k: v for k, v in teams[t].items()},
                   "elo": ratings[t], "matches": count.get(t, 0)} for t in order],
        # [period, phase, teamA, goalsA, teamB, goalsB, decided, penA, penB, eloA_after, eloB_after]
        "matches": [[str(m[period]), m["phase"], idx[m["teamA"]], m["goalsA"], idx[m["teamB"]], m["goalsB"],
                     "pen" if m.get("penA") is not None else "aet" if m.get("et") else "",
                     m.get("penA"), m.get("penB"), h[0], h[1]]
                    for m, h in zip(matches, hist)],
    }
    return out, []


def main():
    outdir = ROOT / "site" / "data"
    outdir.mkdir(parents=True, exist_ok=True)
    failed = False
    for key in COMPS:
        out, bad = build(key)
        if bad:
            failed = True
            print(f"[{key}] {len(bad)} unknown team name(s) — add them (or as an alias) in data/{COMPS[key]['teams']}:")
            for b in bad:
                print(f"    {b}")
            continue
        (outdir / f"{key}.json").write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        print(f"[{key}] {len(out['matches'])} matches, {len(out['teams'])} teams")
    if failed:
        sys.exit(2)
    (outdir / "meta.json").write_text(json.dumps({"built": datetime.now(timezone.utc).isoformat(timespec="minutes")}))


if __name__ == "__main__":
    main()
