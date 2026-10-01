import collections
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import elo
import nationsleague as nl
from common import DATA


def prepared():
    raw = json.loads((DATA / "matches" / "nl.json").read_text(encoding="utf-8"))
    return nl.prepare(raw, json.loads((DATA / "nl_leagues.json").read_text(encoding="utf-8")))


class NationsLeague(unittest.TestCase):
    def test_phases_per_edition(self):
        ms, latest = prepared()
        by = collections.defaultdict(collections.Counter)
        for m in ms:
            by[m["season"]][m["phase"]] += 1
        for season in by:                               # every edition: SF x2, 3rd, final
            self.assertEqual((by[season]["sf"], by[season]["3rd"], by[season]["final"]), (2, 1, 1), season)
        self.assertEqual((by["2018/19"]["A"], by["2018/19"]["D"]), (24, 48))
        self.assertEqual((by["2024/25"]["qf"], by["2024/25"]["poAB"], by["2024/25"]["poBC"]), (8, 8, 8))
        self.assertEqual(collections.Counter(d for t, d in latest.items() if t != "Russia"),
                         {"A": 16, "B": 16, "C": 16, "D": 6})

    def test_finals_and_shootouts(self):
        ms, _ = prepared()
        final = [m for m in ms if m["phase"] == "final" and m["season"] == "2018/19"][0]
        self.assertEqual((final["teamA"], final["teamB"]), ("Portugal", "Netherlands"))
        third = [m for m in ms if m["phase"] == "3rd" and m["season"] == "2018/19"][0]
        self.assertEqual(nl.winner(third), "England")              # won the shoot-out after 0-0
        self.assertEqual(elo.result(third), 0.0)                   # Switzerland (A) lost it

    def test_new_edition_is_inferred(self):
        ms, _ = prepared()
        extra = [{"date": "2026-09-04", "teamA": "Portugal", "goalsA": 2, "teamB": "Spain", "goalsB": 1},
                 {"date": "2026-09-04", "teamA": "Iceland", "goalsA": 0, "teamB": "Wales", "goalsB": 0}]
        raw = json.loads((DATA / "matches" / "nl.json").read_text(encoding="utf-8")) + extra
        out, _ = nl.prepare(raw, json.loads((DATA / "nl_leagues.json").read_text(encoding="utf-8")))
        new = [m for m in out if m["season"] == "2026/27"]
        self.assertEqual([m["phase"] for m in new], ["A", "B"])


if __name__ == "__main__":
    unittest.main()
