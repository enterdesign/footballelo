#!/usr/bin/env python3
"""Refresh data/matches/*.json from openfootball.

usage: sync.py [--worldcup DIR] [--ucl DIR]   (default: shallow-clone both repos)
World Cup is replaced wholesale. For the Champions League seasons from
2011/12 on are replaced; older seasons (not covered by the source) are kept.
"""
import argparse
import json
import subprocess
import tempfile
from pathlib import Path

from common import DATA
import openfootball

UCL_FIRST = "2011/12"


def clone(name, dest):
    subprocess.run(["git", "clone", "-q", "--depth", "1",
                    f"https://github.com/openfootball/{name}", str(dest)], check=True)
    return dest


def dump(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--worldcup")
    ap.add_argument("--ucl")
    args = ap.parse_args()
    with tempfile.TemporaryDirectory() as tmp:
        wc_dir = args.worldcup or clone("worldcup", Path(tmp) / "worldcup")
        ucl_dir = args.ucl or clone("champions-league", Path(tmp) / "champions-league")
        wc = openfootball.parse_worldcup(wc_dir)
        ucl_new = openfootball.parse_ucl(ucl_dir, UCL_FIRST.replace("/", "-"))
    for m in ucl_new:
        m.pop("codeA", None)
        m.pop("codeB", None)
    old = json.loads((DATA / "matches/ucl.json").read_text(encoding="utf-8"))
    ucl = [m for m in old if m["season"] < UCL_FIRST] + ucl_new
    dump(DATA / "matches/wc.json", wc)
    dump(DATA / "matches/ucl.json", ucl)
    print(f"world cup: {len(wc)} matches, champions league: {len(ucl)} matches")


if __name__ == "__main__":
    main()
