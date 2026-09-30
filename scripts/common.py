import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def alias_map(teams):
    """{any known name -> canonical name}. Raises on ambiguous aliases."""
    out = {}
    for canon, info in teams.items():
        for name in [canon, *info.get("aliases", [])]:
            if out.get(name, canon) != canon:
                raise ValueError(f"alias '{name}' is claimed by both '{out[name]}' and '{canon}'")
            out[name] = canon
    return out


def unknown_names(matches, amap):
    return sorted({t for m in matches for t in (m["teamA"], m["teamB"]) if t not in amap})
