import json
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from common import alias_map


def load(key):
    ms = json.loads((ROOT / f"data/matches/{key}.json").read_text(encoding="utf-8"))
    teams = json.loads((ROOT / f"data/teams_{key}.json").read_text(encoding="utf-8"))
    return ms, teams


class Spain(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ms, cls.teams = load("spain")
        cls.n = Counter(m["season"] for m in cls.ms)

    def test_no_missing_seasons(self):
        years = {int(s[:4]) for s in self.n if s < "2026/27"}
        self.assertEqual(sorted(set(range(1928, 2026)) - years), [1936, 1937, 1938])     # Civil War

    def test_sizes(self):
        self.assertEqual(self.n["1928/29"], 90)
        self.assertEqual(self.n["1986/87"], 306)            # the promotion group stage is not rated
        self.assertEqual(self.n["1979/80"], 305)            # Málaga-Salamanca is in no source
        for s in ("1987/88", "2012/13", "2025/26"):
            self.assertEqual(self.n[s], 380, s)

    def test_names_resolve(self):
        names = {t for m in self.ms for t in (m["teamA"], m["teamB"])}
        self.assertEqual(sorted(names - set(alias_map(self.teams))), [])


class France(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ms, cls.teams = load("france")
        cls.n = Counter(m["season"] for m in cls.ms)

    def test_no_missing_seasons(self):
        years = {int(s[:4]) for s in self.n if s < "2026/27"}
        self.assertEqual(sorted(set(range(1932, 2026)) - years), [1939, 1940, 1941, 1942, 1943, 1944])   # war

    def test_filled_gaps(self):
        self.assertEqual(self.n["1937/38"], 240)
        self.assertEqual(self.n["1994/95"], 380)
        self.assertEqual(self.n["2006/07"], 380)
        self.assertEqual(self.n["2019/20"], 279)            # stopped by the pandemic

    def test_names_resolve(self):
        names = {t for m in self.ms for t in (m["teamA"], m["teamB"])}
        self.assertEqual(sorted(names - set(alias_map(self.teams))), [])


class Italy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ms, cls.teams = load("italy")
        cls.n = Counter(m["season"] for m in cls.ms)

    def test_no_missing_seasons(self):
        years = {int(s[:4]) for s in self.n if s < "2026/27"}
        self.assertEqual(sorted(set(range(1929, 2026)) - years), [1943, 1944, 1945])     # war, regional groups

    def test_sizes(self):
        self.assertEqual(self.n["1929/30"], 306)
        self.assertEqual(self.n["1946/47"], 380)
        self.assertEqual(self.n["1947/48"], 380)            # 40 of 420 are in no source
        self.assertEqual(self.n["2025/26"], 380)

    def test_names_resolve(self):
        names = {t for m in self.ms for t in (m["teamA"], m["teamB"])}
        self.assertEqual(sorted(names - set(alias_map(self.teams))), [])
        self.assertFalse([n for n in names if "[awarded]" in n])


if __name__ == "__main__":
    unittest.main()
