""""Recently added matches": what each build found that the previous build did not have.

data/build_state.json  ids of the matches of the latest periods per competition, as of the last recorded build
data/recent.json       batches {"at", "matches": [...]} (last 30 days, at most 400 matches); shown on the home page

A match id is made of the period, the canonical team names and the score (not the source or its spelling), so the same match
fetched from another source - or after a temporary data hiccup - is not reported twice, and a match already shown in an earlier
batch is never listed again. The first recorded build (or one after an id format change) only stores the state.
"""
import json
from collections import Counter
from pathlib import Path

from common import DATA

VERSION = 2          # bump when the id format changes (the next build then only stores a new baseline)
KEEP_PERIODS = 3
MAX_MATCHES = 400
MAX_DAYS = 30


def score_text(m):
    s = f"{m['goalsA']}–{m['goalsB']}"
    if m.get("penA") is not None:
        s += f" ({m['penA']}–{m['penB']} p)"
    elif m.get("penWin"):
        s += " (pens)"
    elif m.get("et"):
        s += " aet"
    return s


def rows_of(key, period, matches, raw_names):
    """Rows of the latest KEEP_PERIODS periods. `matches` carry canonical names, `raw_names` the source names."""
    last = sorted({str(m[period]) for m in matches})[-KEEP_PERIODS:]
    seen, out = Counter(), []
    for m, (ra, rb) in zip(matches, raw_names):
        p = str(m[period])
        if p not in last:
            continue
        base = f"{p}|{m['teamA']}|{m['teamB']}|{m['goalsA']}-{m['goalsB']}"
        seen[base] += 1
        out.append({"id": f"{base}#{seen[base]}", "c": key, "p": p, "a": m["teamA"], "b": m["teamB"],
                    "s": score_text(m), "d": m.get("date", "")})
    return out


def shown(batches):
    return {(m["c"], m["p"], m["a"], m["b"], m["s"]) for b in batches for m in b["matches"]}


def dedupe(batches):
    """Oldest batch wins: a match is listed once."""
    seen, out = set(), []
    for b in reversed(batches):
        keep = []
        for m in b["matches"]:
            k = (m["c"], m["p"], m["a"], m["b"], m["s"])
            if k not in seen:
                seen.add(k)
                keep.append(m)
        if keep:
            out.append({**b, "matches": keep})
    return list(reversed(out))


def update(state, batches, rows_by_comp, now):
    """(new state, new batches, new matches). First run (or an older state format): only the state."""
    batches = dedupe(batches)
    new_state = {"_v": VERSION, **{k: v for k, v in state.items() if k != "_v"}}
    baseline = state.get("_v") == VERSION
    before = shown(batches)
    fresh = []
    for comp, rows in rows_by_comp.items():
        if baseline and comp in state:
            known = set(state[comp])
            fresh += [{k: v for k, v in r.items() if k != "id"} for r in rows
                      if r["id"] not in known and (r["c"], r["p"], r["a"], r["b"], r["s"]) not in before]
        new_state[comp] = [r["id"] for r in rows]
    if not baseline or not fresh:
        return new_state, batches, []
    batches = [{"at": now, "matches": fresh}] + batches
    kept, total = [], 0
    for b in batches:                                   # newest first; cap by age and size
        age = (_dt(now) - _dt(b["at"])).days
        if age > MAX_DAYS or total >= MAX_MATCHES:
            break
        kept.append(b)
        total += len(b["matches"])
    return new_state, kept, fresh


def _dt(s):
    from datetime import datetime
    return datetime.fromisoformat(s)


def record(rows_by_comp, now, data=DATA):
    state_f, recent_f = Path(data) / "build_state.json", Path(data) / "recent.json"
    state = json.loads(state_f.read_text(encoding="utf-8")) if state_f.exists() else {}
    batches = json.loads(recent_f.read_text(encoding="utf-8")).get("batches", []) if recent_f.exists() else []
    new_state, batches, fresh = update(state, batches, rows_by_comp, now)
    state_f.write_text(json.dumps(new_state, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    recent_f.write_text(json.dumps({"batches": batches}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return fresh
