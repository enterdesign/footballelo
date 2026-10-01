"""One ranking over the Champions League, Europa League and Conference League.

Every club has one rating; each match is rated with the K of its own competition and stage
(phase keys are prefixed: ucl_group, el_r16, conf_final ...). Club lists are merged by name (same loose
name and country = same club), so a club that plays in several competitions is one entry.
Within a season the matches are ordered by stage (group/league phase, play-offs, round of 16 ...), then competition.
"""
from common import DATA, alias_map, load, nk, unknown_names

PARTS = ("ucl", "el", "conf")
PREFIX = {"ucl": "CL", "el": "EL", "conf": "CF"}
STAGE = {"group": 0, "po": 1, "r32": 1, "r16": 2, "qf": 3, "sf": 4, "3rd": 5, "final": 5}


def merge_teams(parts):
    """({name: info}, {comp: {comp canonical name: merged name}})."""
    merged, index, rename = {}, {}, {}
    for comp in PARTS:
        rename[comp] = {}
        for name, e in sorted(parts[comp].items()):
            compat = lambda t: not e.get("country") or not merged[t].get("country") or e["country"] == merged[t]["country"]
            target = name if name in merged and compat(name) else None
            if target is None:
                for cand in index.get(nk(name), []):
                    if compat(cand):
                        target = cand
                        break
            if target is None:
                new = name if name not in merged else f"{name} ({e.get('country') or 'other'})"
                merged[new] = {k: v for k, v in e.items() if k != "aliases"}
                merged[new]["aliases"] = [name] if new != name else []
                index.setdefault(nk(name), []).append(new)
                target = new
            else:
                t = merged[target]
                for k in ("code", "country", "logo", "note"):
                    if not t.get(k) and e.get(k):
                        t[k] = e[k]
                if name != target:
                    t["aliases"] = sorted({*t["aliases"], name})
            rename[comp][name] = target
    return merged, rename


def prepare(apply_overrides):
    """(teams, phases, matches, unknown names) of the combined ranking."""
    team_files = {c: load(DATA / f"teams_{c}.json") for c in PARTS}
    all_phases = load(DATA / "phases.json")
    teams, rename = merge_teams(team_files)
    phases = {}
    for comp in PARTS:
        for k, p in all_phases[comp].items():
            phases[f"{comp}_{k}"] = {**p, "label": f"{PREFIX[comp]} {p['label']}"}
    overrides = load(DATA / "overrides.json")
    keyed, bad = [], []
    for ci, comp in enumerate(PARTS):
        amap = alias_map(team_files[comp])
        ms = apply_overrides(load(DATA / "matches" / f"{comp}.json"), overrides.get(comp, {}), "season")
        unknown = unknown_names(ms, amap)
        if unknown:
            bad += [f"[{comp}] {n}" for n in unknown]
            continue
        for i, m in enumerate(ms):
            m = {**m, "teamA": rename[comp][amap[m["teamA"]]], "teamB": rename[comp][amap[m["teamB"]]],
                 "phase": f"{comp}_{m['phase']}"}
            keyed.append(((str(m["season"]), STAGE[m["phase"].split("_", 1)[1]], ci, i), m))
    keyed.sort(key=lambda x: x[0])
    return teams, phases, [m for _, m in keyed], bad
