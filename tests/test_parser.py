"""Integration tests for parsing, AST construction, semantic checks, and TAC."""
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

    def test_tac_emits_arithmetic_and_return(self):
        result = self.run_parser("int main(void) { int a = 2; int b = 3; int c; c = a + b * 4; return c; }", "--tac")
        self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
        output = result.stdout.decode()
        self.assertIn("# Three-address code (TAC)", output)
        self.assertIn("t1 = b * 4", output)
        self.assertIn("t2 = a + t1", output)
        self.assertIn("c = t2", output)
        self.assertIn("return c", output)

    def test_tac_emits_if_labels(self):
        result = self.run_parser("int main(void) { int x = 1; if (x) x = x + 1; else x = 0; return x; }", "--tac")
        self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
        output = result.stdout.decode()
        self.assertIn("ifFalse x goto L_else_", output)
        self.assertIn("L_end_", output)

    def test_undeclared_variable_is_semantic_error(self):
        result = self.run_parser("int main(void) { missing = 2; return 0; }")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"SEM002", result.stderr)

    def test_same_scope_redeclaration_is_semantic_error(self):
        result = self.run_parser("int main(void) { int value; int value; return 0; }")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"SEM001", result.stderr)

    def test_incompatible_return_type_is_semantic_error(self):
        result = self.run_parser('int main(void) { return "not an integer"; }')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"SEM008", result.stderr)

    def test_nested_scope_can_shadow_outer_variable(self):
        result = self.run_parser("int main(void) { int value; { int value; value = 2; } return 0; }")
        self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))

if __name__ == "__main__":
    unittest.main()
