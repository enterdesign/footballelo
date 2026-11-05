import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import logos

CLUB = ('<table class="infobox vcard"><tr><td><img src="//upload.wikimedia.org/wikipedia/en/thumb/8/8c/Valenciennes_FC.svg/200px-Valenciennes_FC.svg.png?utm_source=en.wikipedia.org&amp;utm_campaign=parser"></td></tr>'
        '<tr><th>Full name</th><td>Valenciennes Football Club</td></tr><tr><th>Ground</th><td>Stade du Hainaut</td></tr></table>')
CITY = '<table class="infobox ib-settlement"><tr><td><img src="//upload.wikimedia.org/x/Flag_of_Rouen.png"></td></tr><tr><th>Population</th><td>110,000</td></tr></table>'


class Infobox(unittest.TestCase):
    def run_with(self, html):
        orig = logos.wiki
        logos.wiki = lambda *a, **k: {"parse": {"text": {"*": html}}}
        try:
            return logos.infobox_image("x")
        finally:
            logos.wiki = orig

    def test_crest_of_a_club_article_as_a_clean_250px_url(self):
        self.assertEqual(self.run_with(CLUB), "https://upload.wikimedia.org/wikipedia/en/thumb/8/8c/Valenciennes_FC.svg/250px-Valenciennes_FC.svg.png")

    def test_a_city_article_is_not_a_crest(self):
        self.assertIsNone(self.run_with(CITY))


if __name__ == "__main__":
    unittest.main()
