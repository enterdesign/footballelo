import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import combined as cb


class Merge(unittest.TestCase):
    def test_same_club_is_one_entry(self):
        parts = {"ucl": {"Chelsea": {"country": "England", "code": "ENG", "logo": "x.png", "aliases": ["Chelsea FC"]}},
                 "el": {"Chelsea F.C.": {"country": "England", "code": "ENG", "aliases": []},
                        "Dinamo": {"country": "Croatia", "aliases": []}},
                 "conf": {"Dinamo": {"country": "Serbia", "aliases": []}}}
        teams, rename = cb.merge_teams(parts)
        self.assertEqual(rename["el"]["Chelsea F.C."], "Chelsea")
        self.assertEqual(teams["Chelsea"]["logo"], "x.png")
        self.assertEqual(rename["conf"]["Dinamo"], "Dinamo (Serbia)")      # same name, other country: a different club
        self.assertEqual(len(teams), 3)


if __name__ == "__main__":
    unittest.main()
