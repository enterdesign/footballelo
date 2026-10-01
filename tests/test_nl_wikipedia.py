import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import nl_wikipedia as w

BOX = """<div itemscope="" class="footballbox" id="Italy_v_Belgium" style="color:inherit">
<div class="fleft"><time><div class="fdate">25&#160;September&#160;2026<span style="display: none;">&#160;(<span class="bday dtstart published updated itvstart">2026-09-25</span>)</span></div><div class="ftime">20:45</div></time></div><table class="fevent"><tbody><tr itemprop="name">
<th class="fhome" itemprop="homeTeam"><span itemprop="name"><a href="/wiki/Italy_national_football_team" title="Italy national football team">Italy</a><span class="flagicon">&#160;<span><a href="/wiki/Italy"><img alt="" src="//x/y.png"/></a></span></span></span></th>
<th class="fscore"><a href="/wiki/report">2–1</a></th>
<th class="faway"><span itemprop="name"><span class="flagicon"><a href="/wiki/Belgium"><img alt=""/></a></span>&#160;<a href="/wiki/Belgium_national_football_team">Belgium</a></span></th></tr></tbody></table></div>
<div itemscope="" class="footballbox"><div class="fleft"><div class="fdate"><span class="bday">2026-10-02</span></div></div><table><tr>
<th class="fhome"><a href="/wiki/Spain">Spain</a></th><th class="fscore">v</th><th class="faway"><a href="/wiki/France">France</a></th></tr></table></div>
<div itemscope="" class="footballbox"><div class="fleft"><div class="fdate"><span class="bday">2027-03-28</span></div></div><table><tr>
<th class="fhome"><a href="/wiki/Spain">Spain</a></th><th class="fscore">1–1 <small>(a.e.t.)</small></th><th class="faway"><a href="/wiki/France">France</a></th></tr></table>
<div class="fright">Penalties <b>3–4</b></div></div>"""


class Parse(unittest.TestCase):
    def test_boxes(self):
        ms = w.parse_boxes(BOX)
        self.assertEqual(ms[0], {"date": "2026-09-25", "teamA": "Italy", "goalsA": 2, "teamB": "Belgium", "goalsB": 1})
        self.assertEqual(len(ms), 2)                      # the unplayed box is skipped
        self.assertEqual((ms[1]["teamA"], ms[1]["penWin"]), ("Spain", "B"))


if __name__ == "__main__":
    unittest.main()
