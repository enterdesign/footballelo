import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import uefa_wikipedia as uw

PAGE = """<div class="mw-heading mw-heading3"><h3 id="Round_of_16">Round of 16</h3></div>
<div itemscope="" class="footballbox"><div class="fleft"><div class="fdate"><span class="bday">2019-03-07</span></div></div><table><tr>
<th class="fhome"><span itemprop="name"><a href="/wiki/Arsenal_F.C." title="Arsenal F.C.">Arsenal</a><span class="flagicon"><img src="//x/Flag_of_England.svg/23px-Flag_of_England.svg.png"/></span></span></th>
<th class="fscore">3–0</th>
<th class="faway"><span class="flagicon"><img src="//x/Flag_of_France.svg/23px.png"/></span> <a href="/wiki/Stade_Rennais_F.C.">Rennes</a></th></tr></table></div>
<div class="mw-heading mw-heading3"><h3 id="Final">Final</h3></div>
<div itemscope="" class="footballbox"><div class="fleft"><div class="fdate"><span class="bday">2021-05-26</span></div></div><table><tr>
<th class="fhome"><a href="/wiki/Villarreal_CF">Villarreal</a></th><th class="fscore">1–1 <small>(a.e.t.)</small></th><th class="faway"><a href="/wiki/Manchester_United_F.C.">Manchester United</a></th></tr></table>
<div class="fright">Penalties <b>11–10</b></div></div>"""


class Parse(unittest.TestCase):
    def test_stage_titles_and_pens(self):
        ms, info = uw.parse_page(PAGE, "2018/19")
        self.assertEqual((ms[0]["phase"], ms[0]["teamA"], ms[0]["teamB"], ms[0]["goalsA"]), ("r16", "Arsenal F.C.", "Stade Rennais F.C.", 3))
        self.assertEqual((ms[1]["phase"], ms[1]["et"], ms[1]["penA"], ms[1]["penB"]), ("final", True, 11, 10))
        self.assertEqual(info["Arsenal F.C."]["country"], {"England": 1})
        self.assertEqual(info["Stade Rennais F.C."]["shown"], {"Rennes": 1})

    def test_fixed_phase_and_titles(self):
        ms, _ = uw.parse_page(PAGE, "2024/25", phase="group")
        self.assertEqual({m["phase"] for m in ms}, {"group"})
        self.assertEqual(uw.titles("conf", 2024)[0], "2024–25 UEFA Conference League league phase")
        self.assertEqual(uw.titles("conf", 2022)[1], "2022–23 UEFA Europa Conference League knockout phase")
        self.assertEqual(uw.titles("el", 2012)[0], "2012–13 UEFA Europa League group stage")


if __name__ == "__main__":
    unittest.main()
