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
        h = seo.page("pl", DATA)
        self.assertIn("<title>Test League ELO ranking – football ELO ratings since 1992/93</title>", h)
        self.assertIn("from 1992/93 to 2026/27", h)
        self.assertIn("A &amp; B", h)
        self.assertIn("About this football ELO ranking", h)
        self.assertIn('rel="canonical" href="https://enterdesign.github.io/footballelo/rankings/premier-league.html"', h)

    def test_search_phrases_are_in_the_titles_of_the_matching_pages(self):
        self.assertIn("<title>Champions League ELO ranking – ELO ratings of every club since 1992/93</title>", seo.page("ucl", DATA))
        self.assertIn("<title>World football ELO ratings – national team ELO ranking since 1992/93</title>", seo.page("wc", DATA))
        self.assertIn("<title>UEFA club ELO ranking: Champions League, Europa League &amp; Conference League</title>", seo.page("uefa", DATA))

    def test_spanish_page_with_hreflang_and_links_to_the_app(self):
        h = seo.page("ucl", DATA, "es")
        self.assertIn("<html lang=\"es\">", h)
        self.assertIn("<title>Ranking Elo – Liga de Campeones: clasificación Elo de fútbol desde 1992/93</title>", h)
        self.assertIn('hreflang="en" href="https://enterdesign.github.io/footballelo/rankings/champions-league.html"', h)
        self.assertIn('hreflang="es" href="https://enterdesign.github.io/footballelo/es/rankings/liga-de-campeones.html"', h)
        self.assertIn('href="../../#ucl"', h)
        self.assertIn("A &amp; B", h)

    def test_spanish_home_links_every_ranking_and_is_in_the_sitemap(self):
        h = seo.home_es({"pl": "X (1700)"})
        for slug in seo.SLUGS_ES.values():
            self.assertIn(f"rankings/{slug}.html", h)
            self.assertIn(f"es/rankings/{slug}.html", seo.sitemap())
        self.assertIn("https://enterdesign.github.io/footballelo/es/</loc>", seo.sitemap())
        self.assertIn("líder actual: X (1700)", h)

    def test_every_ranking_is_linked_from_the_home_page_and_listed_in_the_sitemap(self):
        index = (Path(__file__).resolve().parent.parent / "site" / "index.html").read_text(encoding="utf-8")
        for slug in seo.SLUGS.values():
            self.assertIn(f"rankings/{slug}.html", index)
            self.assertIn(f"rankings/{slug}.html", seo.sitemap())

    def test_update_page_is_private_and_holds_no_secret(self):
        root = Path(__file__).resolve().parent.parent / "site"
        page = (root / "update.html").read_text(encoding="utf-8")
        self.assertIn('content="noindex', page)
        self.assertNotIn("update.html", seo.sitemap())
        for marker in ("github_pat_", "ghp_", "ghs_"):
            self.assertNotIn(marker, page)


if __name__ == "__main__":
    unittest.main()
