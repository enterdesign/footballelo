import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import wikipedia_pl as wp

SAMPLE = """Intro text
{{#invoke:sports results|main
|matches_style=FBR|solid_cell=grey
|team1=WIS|team2=KAT|team3=POG

|name_WIS=[[Wisła Kraków]]
|match_WIS_KAT=3–0
|match_WIS_POG=0–2

|name_KAT=[[1. FC Kattowitz]]
|match_KAT_WIS=0–2
|match_KAT_POG=1–0

|name_POG=[[Pogoń Lwów (1904)|Pogoń Lwów]]
|match_POG_WIS=4–1
|match_POG_KAT={{nowrap|0–3}}
|source=Somewhere
}}
more text {{other|template}}
{{#invoke:sports results|main|team1=A|team2=B|name_A=[[Legia Warsaw]]|name_B=[[Ruch Chorzów]]
|match_A_B=1–1
|match_B_A=2–0
}}
"""


class Titles(unittest.TestCase):
    def test_season_label(self):
        self.assertEqual(wp.season_label("1927 Ekstraklasa"), "1927")
        self.assertEqual(wp.season_label("1978–79 Ekstraklasa"), "1978/79")
        self.assertEqual(wp.season_label("1999–2000 Ekstraklasa"), "1999/00")
        self.assertIsNone(wp.season_label("Ekstraklasa"))
        self.assertIsNone(wp.season_label("2024–25 Ekstraklasa squads"))


class Parse(unittest.TestCase):
    def test_club_uses_link_target_without_disambiguation(self):
        self.assertEqual(wp.club("[[Pogoń Lwów (1904)|Pogoń Lwów]]"), ("Pogoń Lwów", "Pogoń Lwów"))
        self.assertEqual(wp.club("[[Union Touring Łódź|Klub Turystów Łódź]]"), ("Union Touring Łódź", "Klub Turystów Łódź"))
        self.assertEqual(wp.club("[[Legia Warsaw]]"), ("Legia Warsaw", "Legia Warsaw"))

    def test_two_blocks_and_scores(self):
        ms = wp.parse_season(SAMPLE, "1927")
        by = {(m["teamA"], m["teamB"]): (m["goalsA"], m["goalsB"]) for m in ms}
        self.assertEqual(len(ms), 6 + 2)
        self.assertEqual(by[("Wisła Kraków", "1. FC Kattowitz")], (3, 0))
        self.assertEqual(by[("Pogoń Lwów", "1. FC Kattowitz")], (0, 3))    # nested template inside the value
        self.assertEqual(by[("Ruch Chorzów", "Legia Warsaw")], (2, 0))
        self.assertTrue(all(m["phase"] == "league" and m["season"] == "1927" for m in ms))


if __name__ == "__main__":
    unittest.main()
