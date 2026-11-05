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

    def test_translated_pages_have_hreflang_and_link_to_the_app_of_their_language(self):
        titles = {"es": "Ranking Elo – Liga de Campeones: clasificación Elo de fútbol desde 1992/93",
                  "pt": "Ranking Elo – Liga dos Campeões: classificação Elo de futebol desde 1992/93",
                  "pl": "Ranking Elo – Liga Mistrzów: punktacja Elo w piłce nożnej od 1992/93"}
        for lang, title in titles.items():
            h = seo.page("ucl", DATA, lang)
            self.assertIn(f'<html lang="{lang}">', h)
            self.assertIn(f"<title>{title}</title>", h)
            for l in seo.LANGS:
                self.assertIn(f'hreflang="{l}" href="{seo.url_of("ucl", l)}"', h)
            self.assertIn('hreflang="x-default" href="https://enterdesign.github.io/footballelo/rankings/champions-league.html"', h)
            self.assertIn('href="../#ucl"', h)
            self.assertIn("A &amp; B", h)
        self.assertIn("rankings/liga-dos-campeoes.html", seo.url_of("ucl", "pt"))
        self.assertIn("pl/rankings/liga-mistrzow.html", seo.url_of("ucl", "pl"))

    def test_language_app_shells_are_the_english_page_with_translated_texts_and_paths(self):
        index = (Path(__file__).resolve().parent.parent / "site" / "index.html").read_text(encoding="utf-8")
        for lang in seo.LANGS[1:]:
            h = seo.shell(index, lang)
            for marker in (f'<html lang="{lang}">', 'href="../style.css"', f'window.LANG = "{lang}"; window.ROOT = "../"', 'src="../app.js"', 'src="../i18n.js"',
                           'href="../update.html"', f'rel="canonical" href="https://enterdesign.github.io/footballelo/{lang}/"', "url('../img/home.jpg')",
                           seo.TX[lang]["all"], f'<div class="eyebrow">{seo.TX[lang]["eyebrow"]}</div>', 'hreflang="x-default" href="https://enterdesign.github.io/footballelo/"'):
                self.assertIn(marker, h, (lang, marker))
            for k, slug in seo.SLUGS_BY[lang].items():
                self.assertIn(f'href="rankings/{slug}.html"', h)
                self.assertIn(seo.url_of(k, lang), seo.sitemap())
            self.assertNotIn("World Cup · European", h)
            self.assertEqual(h.count('data-l="'), 4)
        for lang in seo.LANGS:
            self.assertIn(f"{seo.home_url(lang)}</loc>", seo.sitemap())
        self.assertEqual(seo.sitemap().count("<loc>"), 4 * 15)

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
