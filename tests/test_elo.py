import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import elo
import openfootball as of

PH = {"group": {"k": 8}, "final": {"k": 32}}


class Result(unittest.TestCase):
    def test_penalty_winner_wins(self):
        m = {"goalsA": 1, "goalsB": 1, "penA": 4, "penB": 3}
        self.assertEqual(elo.result(m), 1.0)
        self.assertEqual(elo.result({"goalsA": 1, "goalsB": 1, "penA": 3, "penB": 4}), 0.0)

    def test_draw_and_win(self):
        self.assertEqual(elo.result({"goalsA": 0, "goalsB": 0}), 0.5)
        self.assertEqual(elo.result({"goalsA": 2, "goalsB": 1}), 1.0)

    def test_shootout_winner_gains_points(self):
        r, _, _ = elo.run([{"teamA": "A", "teamB": "B", "goalsA": 1, "goalsB": 1, "penA": 5, "penB": 4, "phase": "final"}], PH)
        self.assertEqual((r["A"], r["B"]), (1616, 1584))


class Parser(unittest.TestCase):
    def test_wc_variants(self):
        p = of.parse_wc_match
        self.assertEqual(p("  Germany 1-1 a.e.t. (1-1, 0-1), 3-4 pen. Paraguay   @ Boston")["penB"], 4)
        m = p("Sun Jul 19 \n") or p("  (104) 15:00 UTC-4  Spain 1-0 a.e.t. (0-0, 0-0) Argentina    @ New York")
        self.assertEqual((m["teamA"], m["goalsA"], m["teamB"], m["goalsB"], m["et"]), ("Spain", 1, "Argentina", 0, True))
        m = p("Thu Jun 12   Brazil v Croatia   3-1 (1-1)  @ Sao Paulo") or p("  17:00 UTC-3  Brazil v Croatia   3-1 (1-1)  @ Sao Paulo")
        self.assertEqual((m["teamA"], m["teamB"]), ("Brazil", "Croatia"))
        m = p("Mon Jun 26    Switzerland  0-3 pen. 0-0 a.e.t. (0-0)   Ukraine  @ Koeln")
        self.assertEqual((m["penA"], m["penB"], m["teamB"]), (0, 3, "Ukraine"))
        self.assertIsNone(p("  (Kylian Mbappe 48', 66' Bradley Barcola 54')"))

    def test_ucl_line(self):
        import tempfile
        txt = "▪ Finals, Final\n  Sat May 30 2026\n    18:00  Paris Saint-Germain FC (FRA) v Arsenal FC (ENG)  4-3 pen. 1-1 a.e.t. (1-1, 0-1)\n"
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
            f.write(txt)
        m = of.parse_ucl_file(f.name, "2025/26")[0]
        self.assertEqual((m["phase"], m["goalsA"], m["penA"], m["penB"]), ("final", 1, 4, 3))


if __name__ == "__main__":
    unittest.main()
