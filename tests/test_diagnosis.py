import unittest
from diagnosis.diagnose import diagnose
from diagnosis.repair import repair_source

class DiagnosisTests(unittest.TestCase):
    def test_unmatched_open_brace(self):
        self.assertTrue(any(f.code == "SYN002" for f in diagnose("int main() {\n return 0;\n")))
    def test_unmatched_closing_brace(self):
        self.assertTrue(any(f.code == "SYN001" for f in diagnose("int main() { return 0; }}")))
    def test_possible_missing_semicolon(self):
        self.assertTrue(any(f.code == "SYN003" for f in diagnose("int main() {\n int x = 5\n return x;\n}")))
    def test_ignores_delimiters_in_strings_comments(self):
        findings = diagnose('int main() { printf("}"); /* ( ] */ return 0; }')
        self.assertFalse(any(f.code in {"SYN001", "SYN002"} for f in findings))
    def test_repairs_simple_return(self):
        fixed, repairs = repair_source("int main() {\n return 0\n}\n")
        self.assertIn("return 0;", fixed)
        self.assertEqual(len(repairs), 1)
    def test_control_header_not_repaired(self):
        source = "if (x == 1)\n"
        self.assertEqual(repair_source(source), (source, []))

if __name__ == "__main__":
    unittest.main()
