import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import recent


def m(a, b, ga, gb, season="2026/27", phase="group"):
    return {"season": season, "phase": phase, "teamA": a, "teamB": b, "goalsA": ga, "goalsB": gb}


def rows(*ms):
    return {"ucl": recent.rows_of("ucl", "season", list(ms), [(x["teamA"], x["teamB"]) for x in ms])}


class Recent(unittest.TestCase):
    def test_first_build_only_stores_the_state_then_new_matches_are_reported(self):
        with tempfile.TemporaryDirectory() as d:
            a, b, c = m("A", "B", 1, 0), m("C", "D", 2, 2), m("E", "F", 0, 1)
            self.assertEqual(recent.record(rows(a, b), "2026-10-01T05:00+00:00", d), [])
            fresh = recent.record(rows(a, b, c), "2026-10-02T05:00+00:00", d)
            self.assertEqual([(x["a"], x["b"], x["s"]) for x in fresh], [("E", "F", "0–1")])
            self.assertEqual(recent.record(rows(a, b, c), "2026-10-03T05:00+00:00", d), [])      # nothing new
            batches = json.loads((Path(d) / "recent.json").read_text())["batches"]
            self.assertEqual(len(batches), 1)
            self.assertEqual(batches[0]["at"], "2026-10-02T05:00+00:00")

    def test_identical_legs_are_counted_separately_and_old_batches_expire(self):
        with tempfile.TemporaryDirectory() as d:
            a = m("A", "B", 1, 0)
            recent.record(rows(a), "2026-09-01T05:00+00:00", d)
            fresh = recent.record(rows(a, dict(a)), "2026-09-02T05:00+00:00", d)                 # same pair and score twice
            self.assertEqual(len(fresh), 1)
            recent.record(rows(a, dict(a), m("C", "D", 1, 1)), "2026-11-15T05:00+00:00", d)
            batches = json.loads((Path(d) / "recent.json").read_text())["batches"]
            self.assertEqual([b["at"][:10] for b in batches], ["2026-11-15"])                    # September batch is older than 30 days


if __name__ == "__main__":
    unittest.main()
