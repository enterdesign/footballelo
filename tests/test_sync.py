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

    def test_new_matches_are_added_even_when_the_source_is_short(self):
        mk = lambda n: [{"season": "2026/27", "phase": "league", "teamA": f"A{i}", "teamB": f"B{i}"} for i in range(n)]
        canon = {"A0": "Same"}.get                                 # spelling variants of one team count as one
        old = mk(60)
        fresh = mk(56) + [{"season": "2026/27", "phase": "league", "teamA": "N1", "teamB": "N2"},
                          {"season": "2026/27", "phase": "league", "teamA": "A0", "teamB": "B0"}]
        out = sync.keep_if_larger(old, fresh, "2026/27", "PL", lambda t: canon(t) or t)
        cur = [m for m in out if m["season"] == "2026/27"]
        self.assertEqual(len(cur), 61)                             # 60 stored + the one genuinely new match
        self.assertIn(("N1", "N2"), {(m["teamA"], m["teamB"]) for m in cur})


if __name__ == "__main__":
    unittest.main()
