import json
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import germany
from common import alias_map


class Parse(unittest.TestCase):
    def test_openfootball_line(self):
        import england
        self.assertEqual(england.parse_line("   20:30  Borussia Mönchengladbach v Bayer 04 Leverkusen      2-3 (0-2)"),
                         ("Borussia Mönchengladbach", 2, "Bayer 04 Leverkusen", 3))


class StoredData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ms = json.loads((ROOT / "data/matches/bundesliga.json").read_text(encoding="utf-8"))
        cls.teams = json.loads((ROOT / "data/teams_bundesliga.json").read_text(encoding="utf-8"))

    def test_complete_seasons(self):
        n = Counter(m["season"] for m in self.ms)
        self.assertEqual(n["1963/64"], 240)           # 16 clubs
        self.assertEqual(n["1991/92"], 340)           # 20 clubs, first season with East German clubs
        for s, c in n.items():
            if "1965/66" <= s <= "2025/26" and s != "1991/92":
                self.assertEqual(c, 306, s)

    def test_names_resolve(self):
        am = alias_map(self.teams)
        names = {t for m in self.ms for t in (m["teamA"], m["teamB"])}
        self.assertEqual(sorted(names - set(am)), [])

    def test_sources_do_not_overlap(self):
        self.assertEqual(min(m["season"] for m in self.ms), "1963/64")
        self.assertEqual(germany.FIRST_OF, "2010/11")


if __name__ == "__main__":
    unittest.main()
