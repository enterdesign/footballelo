#!/usr/bin/env python3
"""Build site/data/{ucl,wc,pl,ekstraklasa,nl}.json (ranking + per-match history) from data/.

Exits with status 2 (and a readable report) if a team name has no entry in
data/teams_*.json, so new names are never guessed.
"""
import json
import sys
from datetime import datetime, timezone

from common import DATA, ROOT, alias_map, load, unknown_names
import elo
import nationsleague
import tournaments

COMPS = {
    "ucl": {"teams": "teams_ucl.json", "period": "season", "title": "UEFA Champions League"},
    "wc": {"teams": "teams_wc.json", "period": "year", "title": "FIFA World Cup"},
    "pl": {"teams": "teams_pl.json", "period": "season", "title": "Premier League (First Division 1888–1992)",
           # era chips are filters over the years (one continuous rating per club)
           "eras": [{"id": "pre", "label": "Pre-Premier League era", "to": "1991/92"},
                    {"id": "pl", "label": "Premier League era", "from": "1992/93"}]},
    "ekstraklasa": {"teams": "teams_ekstraklasa.json", "period": "season", "title": "Ekstraklasa (I liga 1927–2008)",
                    "eras": [{"id": "pre", "label": "Pre-war (1927–1939)", "to": "1939"},
                             {"id": "post", "label": "Post-war (1948–)", "from": "1948"}],
                    "default_era": "post"},
    "el": {"teams": "teams_el.json", "period": "season", "title": "UEFA Europa League"},
    "conf": {"teams": "teams_conf.json", "period": "season", "title": "UEFA Conference League"},
    "nl": {"teams": "teams_nl.json", "period": "season", "title": "UEFA Nations League"},
    "euro": {"teams": "teams_euro.json", "period": "year", "title": "UEFA European Championship"},
    "copa": {"teams": "teams_copa.json", "period": "year", "title": "Copa América (1993 →)"},
}


def era_ranking(matches, hist, order, period, era):
    """An era is only a filter over the years: the leaderboard shows the clubs that played in that era,
    with their ONE continuous rating as it stood at the end of the era (so a club that played before
    and after a break carries its rating over). Games and delta refer to the era, indexed like `order`."""
    lo, hi = era.get("from", ""), era.get("to", "\uffff")
    inside = [str(m[period]) for m in matches if lo <= str(m[period]) <= hi]
    last = inside[-1]
    cur, count, first_before = {}, {}, {}
    for m, (ea, eb) in zip(matches, hist):
        p = str(m[period])
        if p > hi:
            break
        for t, e in ((m["teamA"], ea), (m["teamB"], eb)):
            if p >= lo:
                count[t] = count.get(t, 0) + 1
                if p == last and t not in first_before:
                    first_before[t] = cur.get(t, elo.INITIAL)     # rating before the era's last season
            cur[t] = e
    return {"id": era["id"], "label": era["label"], "first": inside[0], "last": last,
            "elo": [cur.get(t, elo.INITIAL) for t in order], "matches": [count.get(t, 0) for t in order],
            "delta": [cur[t] - first_before[t] if t in first_before else 0 for t in order]}


def apply_overrides(matches, ov, period):
    def same(m, r):
        return all(m.get(k) == v for k, v in r.items())
    for r in ov.get("remove", []):
        n = len(matches)
        matches = [m for m in matches if not same(m, r)]
        if len(matches) == n:
            print(f"  warning: override 'remove' matched nothing: {r}", file=sys.stderr)
    return matches + ov.get("add", [])


def pens(m):
    """(penA, penB) for the output; a shoot-out whose score is unknown only records the winner (1-0 / 0-1, shown as "pens")."""
    if m.get("penWin"):
        return (1, 0) if m["penWin"] == "A" else (0, 1)
    return m.get("penA"), m.get("penB")


def build(key):
    cfg = COMPS[key]
    teams = load(DATA / cfg["teams"])
    phases = load(DATA / "phases.json")[key]
    amap = alias_map(teams)
    period = cfg["period"]
    matches = load(DATA / "matches" / f"{key}.json")
    division = {}
    if key == "nl":                     # raw results -> editions, division phases
        matches, division = nationsleague.prepare(matches, load(DATA / "nl_leagues.json"), lambda t: amap.get(t, t))
    elif key in ("euro", "copa"):       # dated results -> editions, stages
        matches = tournaments.prepare(key, matches)
    matches = apply_overrides(matches, load(DATA / "overrides.json").get(key, {}), period)
    bad = unknown_names(matches, amap)
    if bad:
        return None, bad
    matches.sort(key=lambda m: str(m[period]))          # stable: file order inside a period
    for m in matches:
        m["teamA"], m["teamB"] = amap[m["teamA"]], amap[m["teamB"]]
        if m["phase"] not in phases:
            raise SystemExit(f"{key}: unknown phase {m['phase']!r} in {m}")
    division = {amap[t]: d for t, d in division.items() if t in amap}
    ratings, count, hist = elo.run(matches, phases, seed=teams)
    order = sorted(ratings, key=lambda t: (-ratings[t], t))
    idx = {t: i for i, t in enumerate(order)}
    out = {
        "title": cfg["title"],
        "phases": phases,
        "teams": [{"name": t, **{k: v for k, v in teams[t].items()}, **({"division": division[t]} if t in division else {}),
                   "elo": ratings[t], "matches": count.get(t, 0)} for t in order],
        # [period, phase, teamA, goalsA, teamB, goalsB, decided, penA, penB, eloA_after, eloB_after]
        "matches": [[str(m[period]), m["phase"], idx[m["teamA"]], m["goalsA"], idx[m["teamB"]], m["goalsB"],
                     "pen" if m.get("penA") is not None else "pw" if m.get("penWin") else "aet" if m.get("et") else "",
                     *pens(m), h[0], h[1]]
                    for m, h in zip(matches, hist)],
    }
    if cfg.get("eras"):
        out["eras"] = [era_ranking(matches, hist, order, period, e) for e in cfg["eras"]]
        if cfg.get("default_era"):
            out["default_era"] = cfg["default_era"]
    return out, []


def main():
    outdir = ROOT / "site" / "data"
    outdir.mkdir(parents=True, exist_ok=True)
    failed = False
    info = {}
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
        info[key] = {"matches": len(out["matches"]), "last": out["matches"][-1][0],
                     "last_matches": sum(1 for m in out["matches"] if m[0] == out["matches"][-1][0])}
    if failed:
        sys.exit(2)
    sync = DATA / "sync.json"
    meta = {"built": datetime.now(timezone.utc).isoformat(timespec="minutes"),
            "synced": load(sync)["synced"] if sync.exists() else None, "comps": info}
    (outdir / "meta.json").write_text(json.dumps(meta))


if __name__ == "__main__":
    main()
