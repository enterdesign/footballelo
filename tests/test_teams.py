import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import seo
import teams

# teams: 0 = "A & B" (club), 1 = "C"; the match rows are [period, phase, a, goals a, b, goals b, how, pens a, pens b, rating a, rating b]
DATA = {"title": "Test League (1990 →)", "phases": {"g": {"label": "GR", "k": 8}},
        "teams": [{"name": "A & B", "elo": 1620, "matches": 3, "country": "Spain"}, {"name": "C", "elo": 1580, "matches": 3}],
        "matches": [["1992/93", "g", 0, 2, 1, 1, "", None, None, 1608, 1592], ["1992/93", "g", 1, 0, 0, 0, "", None, None, 1596, 1604],
                    ["1993/94", "g", 0, 1, 1, 1, "pw", 4, 5, 1620, 1580]]}


class Teams(unittest.TestCase):
    def setUp(self):
        self.ctx = {"datas": {"pl": DATA}, "ents": teams.build_index({"pl": DATA}), "names": {}, "nation_names": set(),
                    "rnames": {l: {"pl": "Test League"} for l in seo.LANGS}}

    def test_index_slug_and_main_ranking(self):
        e = self.ctx["ents"]["A & B"]
        self.assertEqual((e["slug"], e["main"]), ("a-b", "pl"))
        self.assertEqual(teams.slugify("Atlético Madrid"), "atletico-madrid")

    def test_timeline_record_and_penalties(self):
        rows = teams.timeline(DATA, 0)
        self.assertEqual([r[5] for r in rows], ["W", "D", "L"])   # win, goalless draw, 1-1 lost on penalties (4-5)
        self.assertEqual(rows[0][6], 1608)                         # rating after the first match

    def test_page_has_title_escaped_name_numbers_and_links(self):
        h = teams.page(self.ctx["ents"]["A & B"], "en", self.ctx)
        self.assertIn("<title>A &amp; B ELO rating and history since 1992/93</title>", h)
        self.assertIn("ranked <b>1</b> of 2", h)
        self.assertIn('rel="canonical" href="https://enterdesign.github.io/footballelo/teams/a-b.html"', h)
        self.assertIn("<svg", h)                                # chart
        self.assertIn('<a href="c.html">C</a>', h)              # neighbour that has a page of its own
        self.assertNotIn("A & B<", h.split("<body>")[1].replace("A &amp; B", ""))

    def test_other_languages(self):
        for lang, word in (("es", "Elo de A &amp; B"), ("pt", "Elo: A &amp; B"), ("pl", "Elo A &amp; B")):
            h = teams.page(self.ctx["ents"]["A & B"], lang, self.ctx)
            self.assertIn(f"<title>{word}", h)
            for l in seo.LANGS:
                self.assertIn(f'hreflang="{l}" href="{teams.team_url("a-b", l)}"', h)

    def test_generate_writes_pages_links_and_sitemap_urls(self):
        with tempfile.TemporaryDirectory() as tmp:
            links, urls = teams.generate(tmp, {"pl": DATA})
            self.assertTrue((Path(tmp) / "teams" / "a-b.html").exists())
            self.assertTrue((Path(tmp) / "es" / "equipos" / "a-b.html").exists())
            self.assertEqual(links["pl"]["A & B"], "../druzyny/a-b.html")
            self.assertEqual(len(urls), 3 * len(seo.LANGS))                          # two teams and the hub page, in every language
            self.assertIn('href="../teams/a-b.html">A &amp; B</a>', seo.page("pl", DATA, "en", links["en"]))
            self.assertIn("teams/a-b.html", seo.sitemap(urls))

    def test_hub_page_lists_every_team_and_links_to_rankings(self):
        h = teams.hub_page("en", self.ctx)
        self.assertIn("<title>All teams: football ELO ratings</title>", h)
        self.assertIn('<a href="a-b.html">A &amp; B</a>', h)
        self.assertIn('href="../rankings/premier-league.html"', h)
        for lang in seo.LANGS:
            self.assertIn(f'hreflang="{lang}" href="{teams.hub_url(lang)}"', h)
        self.assertEqual(teams.hub_url("pl"), "https://enterdesign.github.io/footballelo/pl/druzyny/")

    def test_sitemaps_are_split_and_indexed(self):
        import xml.etree.ElementTree as ET
        with tempfile.TemporaryDirectory() as tmp:
            links, urls = teams.generate(tmp, {"pl": DATA})
            seo.write_sitemaps(Path(tmp), urls)
            ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
            count = lambda f, tag: len(ET.parse(Path(tmp) / f).getroot().findall(f"{ns}{tag}/{ns}loc"))
            self.assertEqual(count("sitemap-pages.xml", "url"), len(seo.LANGS) * (1 + len(seo.SLUGS)))
            self.assertEqual(count("sitemap-teams.xml", "url"), len(urls))
            self.assertEqual(count("sitemap.xml", "url"), count("sitemap-pages.xml", "url") + len(urls))
            self.assertEqual(count("sitemap-index.xml", "sitemap"), 2)


if __name__ == "__main__":
    unittest.main()
