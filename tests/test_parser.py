"""Integration tests for parsing, AST construction, and semantic checks."""
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
PARSER = ROOT / "compiler" / "build" / "parser"
FIXTURES = ROOT / "tests" / "fixtures"

class ParserTests(unittest.TestCase):
    def run_parser(self, source, *args):
        return subprocess.run([str(PARSER), *args, "-"], input=source.encode(),
            capture_output=True, check=False, cwd=ROOT)

    def test_valid_fixture_parses_and_checks(self):
        source = (FIXTURES / "valid_basic.c").read_text(encoding="utf-8")
        result = self.run_parser(source)
        self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
        self.assertIn(b"analysis successful", result.stdout)

    def test_missing_semicolon_is_rejected(self):
        result = self.run_parser("int main(void) { int value = 4 return value; }")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"SYN100", result.stderr)

    def test_empty_translation_unit_is_accepted(self):
        result = self.run_parser("")
        self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))

    def test_ast_json_contains_function_and_declaration(self):
        result = self.run_parser("int main(void) { int count = 3; return count; }", "--ast")
        self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
        self.assertIn(b'"kind": "translation_unit"', result.stdout)
        self.assertIn(b'"kind": "function"', result.stdout)
        self.assertIn(b'"kind": "declaration"', result.stdout)
        self.assertIn(b'"text": "count"', result.stdout)

    def test_undeclared_variable_is_semantic_error(self):
        result = self.run_parser("int main(void) { missing = 2; return 0; }")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"SEM002", result.stderr)

    def test_same_scope_redeclaration_is_semantic_error(self):
        result = self.run_parser("int main(void) { int value; int value; return 0; }")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"SEM001", result.stderr)

    def test_nested_scope_can_shadow_outer_variable(self):
        result = self.run_parser("int main(void) { int value; { int value; value = 2; } return 0; }")
        self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))

if __name__ == "__main__":
    unittest.main()
