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

    def test_a_match_that_vanishes_for_one_build_and_returns_is_not_reported_again(self):
        with tempfile.TemporaryDirectory() as d:
            a, b, c = m("A", "B", 1, 0), m("C", "D", 2, 2), m("E", "F", 0, 1)
            recent.record(rows(a, b), "2026-10-01T05:00+00:00", d)
            self.assertEqual(len(recent.record(rows(a, b, c), "2026-10-02T05:00+00:00", d)), 1)
            self.assertEqual(recent.record(rows(a, b), "2026-10-03T05:00+00:00", d), [])         # source hiccup: c is gone
            self.assertEqual(recent.record(rows(a, b, c), "2026-10-04T05:00+00:00", d), [])      # ... and back: not new
            self.assertEqual(sum(len(x["matches"]) for x in json.loads((Path(d) / "recent.json").read_text())["batches"]), 1)

    def test_an_old_state_format_only_rebuilds_the_baseline(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "build_state.json").write_text(json.dumps({"ucl": ["old|raw|id#1"]}))
            self.assertEqual(recent.record(rows(m("A", "B", 1, 0)), "2026-10-05T05:00+00:00", d), [])

    def test_existing_duplicates_are_cleaned(self):
        batch = lambda at, *ms: {"at": at, "matches": [{"c": "pl", "p": "2026/27", "a": a, "b": b, "s": "1–0", "d": ""} for a, b in ms]}
        out = recent.dedupe([batch("2026-10-14", ("A", "B"), ("C", "D")), batch("2026-10-12", ("A", "B"))])
        self.assertEqual([(b["at"], len(b["matches"])) for b in out], [("2026-10-14", 1), ("2026-10-12", 1)])


if __name__ == "__main__":
    unittest.main()
