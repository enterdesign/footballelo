import collections
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import tournaments as t
from common import DATA


def prepared(key):
    return t.prepare(key, json.loads((DATA / "matches" / f"{key}.json").read_text(encoding="utf-8")))


class Tournaments(unittest.TestCase):
    def test_euro_formats(self):
        by = collections.defaultdict(collections.Counter)
        for m in prepared("euro"):
            by[m["year"]][m["phase"]] += 1
        self.assertEqual(dict(by["1980"]), {"group": 12, "3rd": 1, "final": 1})
        self.assertEqual(dict(by["1968"]), {"sf": 2, "3rd": 1, "final": 2})      # final replayed
        self.assertEqual(dict(by["2008"]), {"group": 24, "qf": 4, "sf": 2, "final": 1})
        self.assertEqual(dict(by["2020"]), {"group": 36, "r16": 8, "qf": 4, "sf": 2, "final": 1})   # played in 2021
        self.assertEqual(by["2024"]["final"], 1)

    def test_copa_from_1993(self):
        ms = prepared("copa")
        self.assertEqual(min(m["year"] for m in ms), "1993")
        by = collections.defaultdict(collections.Counter)
        for m in ms:
            by[m["year"]][m["phase"]] += 1
        for y, c in by.items():
            self.assertEqual((c["qf"], c["sf"], c["3rd"], c["final"]), (4, 2, 1, 1), y)

    def test_finals(self):
        finals = {m["year"]: (m["teamA"], m["teamB"]) for m in prepared("euro") if m["phase"] == "final"}
        self.assertEqual(set(finals["2024"]), {"Spain", "England"})
        copa = {m["year"]: (m["teamA"], m["teamB"]) for m in prepared("copa") if m["phase"] == "final"}
        self.assertEqual(set(copa["2024"]), {"Argentina", "Colombia"})


if __name__ == "__main__":
    unittest.main()
