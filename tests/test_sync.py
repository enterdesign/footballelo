import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import sync


class RunningSeason(unittest.TestCase):
    def test_a_source_that_returns_fewer_matches_never_shrinks_the_season(self):
        mk = lambda n: [{"season": "2026/27", "teamA": f"A{i}", "teamB": f"B{i}"} for i in range(n)]
        old = mk(60) + [{"season": "2025/26", "teamA": "X", "teamB": "Y"}]
        out = sync.keep_if_larger(old, mk(56) + [{"season": "2025/26", "teamA": "X", "teamB": "Y"}], "2026/27", "PL")
        self.assertEqual(len([m for m in out if m["season"] == "2026/27"]), 60)
        out = sync.keep_if_larger(old, mk(61), "2026/27", "PL")
        self.assertEqual(len(out), 61)


if __name__ == "__main__":
    unittest.main()
