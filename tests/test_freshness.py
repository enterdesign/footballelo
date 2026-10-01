import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import freshness


class Stale(unittest.TestCase):
    feeds = {"ucl": {"n": 10, "changed": "2026-09-01"}, "pl": {"n": 5, "changed": "2026-09-20"},
             "wc": {"n": 1, "changed": "2020-01-01"}, "nl": {"n": 3, "changed": "2026-09-15"}}

    def test_in_season_gap_is_reported(self):
        self.assertEqual(freshness.stale(self.feeds, date(2026, 10, 25)), [("ucl", 54), ("pl", 35), ("nl", 40)])

    def test_summer_break_and_finished_tournaments_are_ignored(self):
        self.assertEqual(freshness.stale(self.feeds, date(2026, 7, 20)), [])

    def test_recent_change_is_fine(self):
        feeds = {"ucl": {"n": 10, "changed": "2026-10-20"}}
        self.assertEqual(freshness.stale(feeds, date(2026, 10, 25)), [])


if __name__ == "__main__":
    unittest.main()
