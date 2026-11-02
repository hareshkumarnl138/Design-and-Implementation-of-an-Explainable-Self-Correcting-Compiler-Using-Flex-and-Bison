import unittest

from compiler.tac_optimizer import build_basic_blocks, optimize_tac


class TacOptimizerTests(unittest.TestCase):
    def test_builds_blocks_and_branch_successors(self):
        tac = [
            "function main:",
            "ifFalse x goto L_else_1",
            "x = 1",
            "goto L_end_2",
            "L_else_1:",
            "x = 2",
            "L_end_2:",
            "return x",
            "end function main",
        ]
        blocks = build_basic_blocks(tac)
        by_name = {block.name: block for block in blocks}
        self.assertIn("L_else_1", by_name)
        self.assertIn("L_end_2", by_name)
        self.assertIn("L_else_1", by_name["B1"].successors)

    def test_constant_folding_and_propagation(self):
        source = "# TAC\nfunction main:\nt1 = 2 + 3\nt2 = t1 * 4\nx = t2\nreturn x\nend function main\n"
        optimized, _ = optimize_tac(source)
        self.assertIn("x = 20", optimized)
        self.assertNotIn("t1 =", optimized)
        self.assertNotIn("t2 =", optimized)

    def test_preserves_side_effects_and_branch_targets(self):
        source = "function main:\nparam x\ncall print, 1\ngoto L1\nL1:\nreturn\nend function main\n"
        optimized, blocks = optimize_tac(source)
        self.assertIn("param x", optimized)
        self.assertIn("call print, 1", optimized)
        self.assertIn("goto L1", optimized)
        self.assertTrue(any(b.name == "L1" for b in blocks))

    def test_does_not_fold_division_by_zero(self):
        optimized, _ = optimize_tac("function main:\nt1 = 4 / 0\nreturn t1\nend function main\n")
        self.assertIn("t1 = 4 / 0", optimized)


if __name__ == "__main__":
    unittest.main()
