import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import seo

DATA = {"title": "Test League", "phases": {"g": {"label": "GR", "k": 8}},
        "teams": [{"name": "A & B", "elo": 1700, "matches": 10, "country": "Spain"},
                  {"name": "C", "elo": 1650, "matches": 9}],
        "matches": [["1992/93", "g", 0, 1, 1, 0, "", None, None, 1608, 1592], ["2026/27", "g", 1, 0, 0, 0, "", None, None, 1600, 1600]]}


class Seo(unittest.TestCase):
    def test_page_has_title_description_and_escaped_table(self):
        h = seo.page("ucl", DATA)
        self.assertIn("<title>Test League ELO ranking – Football ELO</title>", h)
        self.assertIn("from 1992/93 to 2026/27", h)
        self.assertIn("A &amp; B", h)
        self.assertIn('rel="canonical" href="https://enterdesign.github.io/footballelo/rankings/champions-league.html"', h)

    def test_every_ranking_is_linked_from_the_home_page_and_listed_in_the_sitemap(self):
        index = (Path(__file__).resolve().parent.parent / "site" / "index.html").read_text(encoding="utf-8")
        for slug in seo.SLUGS.values():
            self.assertIn(f"rankings/{slug}.html", index)
            self.assertIn(f"rankings/{slug}.html", seo.sitemap())


if __name__ == "__main__":
    unittest.main()
