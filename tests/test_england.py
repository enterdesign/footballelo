import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import england as eng


class ParseLine(unittest.TestCase):
    def test_modern_line(self):
        self.assertEqual(eng.parse_line("    20:00  Liverpool               v AFC Bournemouth      4-2 (1-0)"),
                         ("Liverpool", 4, "AFC Bournemouth", 2))
        self.assertEqual(eng.parse_line("           Sunderland AFC          v West Ham United      3-0 (0-0)"),
                         ("Sunderland AFC", 3, "West Ham United", 0))

    def test_archive_line(self):
        self.assertEqual(eng.parse_line("  Bolton Wanderers FC       3-6  Derby County FC"),
                         ("Bolton Wanderers FC", 3, "Derby County FC", 6))
        self.assertEqual(eng.parse_line("  Everton FC                2-1  Accrington FC (1878-1896)"),
                         ("Everton FC", 2, "Accrington FC (1878-1896)", 1))

    def test_half_time_between_teams(self):
        self.assertEqual(eng.parse_line("  Arsenal FC  2-1 (0-0)  Chelsea FC"), ("Arsenal FC", 2, "Chelsea FC", 1))

    def test_non_match_lines(self):
        for line in ("= English Premier League 2025/26", "Sat Sep 8", "▪ Matchday 1", "  Fri Aug 15 ", ""):
            self.assertIsNone(eng.parse_line(line), line)


if __name__ == "__main__":
    unittest.main()
