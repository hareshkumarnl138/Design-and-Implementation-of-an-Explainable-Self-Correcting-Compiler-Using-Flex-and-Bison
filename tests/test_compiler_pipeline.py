import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PIPELINE = ROOT / "compiler_pipeline.py"
FIXTURE = ROOT / "tests" / "fixtures" / "valid_basic.c"

class CompilerPipelineTests(unittest.TestCase):
    def run_pipeline(self, *args):
        return subprocess.run(
            [sys.executable, str(PIPELINE), str(FIXTURE), *args],
            cwd=ROOT, text=True, capture_output=True, check=False, timeout=20,
        )

    def test_o0_emits_raw_tac(self):
        result = self.run_pipeline("-O0")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("function", result.stdout)
        self.assertIn("return", result.stdout)

    def test_o1_runs_optimizer_and_reports_blocks(self):
        result = self.run_pipeline("-O1", "--blocks", "--report")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("function", result.stdout)
        self.assertIn("Basic blocks and CFG successors", result.stderr)
        self.assertIn("TAC instructions:", result.stderr)

if __name__ == "__main__":
    unittest.main()
