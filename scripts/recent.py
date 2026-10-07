""""Recently added matches": what each build found that the previous build did not have.

data/build_state.json  ids of the matches of the latest periods per competition, as of the last recorded build
data/recent.json       batches {"at", "matches": [...]} (last 30 days, at most 400 matches); shown on the home page

A match id is made of its raw (source) names, so renaming a club in data/teams_*.json does not make old matches look new.
The first recorded build only stores the state (it would otherwise report every match as new).
"""
import json
from collections import Counter
from pathlib import Path

from common import DATA

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
        base = f"{p}|{m['phase']}|{ra}|{rb}|{m['goalsA']}-{m['goalsB']}"
        seen[base] += 1
        out.append({"id": f"{base}#{seen[base]}", "c": key, "p": p, "a": m["teamA"], "b": m["teamB"],
                    "s": score_text(m), "d": m.get("date", "")})
    return out


def update(state, batches, rows_by_comp, now):
    """(new state, new batches, new matches). First run: only the state."""
    new_state = dict(state)
    fresh = []
    for comp, rows in rows_by_comp.items():
        if state and comp in state:
            known = set(state[comp])
            fresh += [{k: v for k, v in r.items() if k != "id"} for r in rows if r["id"] not in known]
        new_state[comp] = [r["id"] for r in rows]
    if not state or not fresh:
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
