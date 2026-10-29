"""Smoke tests for the Bison syntax parser."""
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
PARSER = ROOT / "compiler" / "build" / "parser"
FIXTURES = ROOT / "tests" / "fixtures"

class ParserTests(unittest.TestCase):
    def run_parser(self, source):
        return subprocess.run([str(PARSER), "-"], input=source.encode(),
            capture_output=True, check=False, cwd=ROOT)

    def test_valid_fixture_parses(self):
        source = (FIXTURES / "valid_basic.c").read_text(encoding="utf-8")
        result = self.run_parser(source)
        self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))

    def test_missing_semicolon_is_rejected(self):
        result = self.run_parser("int main(void) { int value = 4 return value; }")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"SYN100", result.stderr)

    def test_empty_translation_unit_is_accepted(self):
        result = self.run_parser("")
        self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))

if __name__ == "__main__":
    unittest.main()
