"""Automated tests for the Flex lexer (Step 1)."""
import json, os, subprocess, unittest
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEXER=os.path.join(ROOT,"compiler","build","lexer")
FIXTURES=os.path.join(ROOT,"tests","fixtures")
def lex(source,*flags):
    data=source if isinstance(source,bytes) else source.encode("utf-8")
    p=subprocess.run([LEXER,"--json",*flags,"-"],input=data,capture_output=True,check=False)
    assert p.returncode in (0,1),p.stderr.decode()
    return json.loads(p.stdout.decode("utf-8")),p.returncode
def types(source,*flags): return [t["type"] for t in lex(source,*flags)[0]["tokens"]]
def codes(source): return [d["code"] for d in lex(source)[0]["diagnostics"]]
class TokenizationTests(unittest.TestCase):
    def test_keywords(self): self.assertEqual(types("int integer _x1 if iffy"),["KW_INT","IDENTIFIER","IDENTIFIER","KW_IF","IDENTIFIER"])
    def test_all_keywords(self):
        src="int float double char void if else while for do return break continue"
        self.assertTrue(all(t.startswith("KW_") for t in types(src))); self.assertEqual(len(types(src)),13)
    def test_integer_literals(self):
        for lit in ["0","42","0xFF","0Xab","077","10u","10UL","0x1fL"]:
            with self.subTest(lit=lit): self.assertEqual(types(lit),["INT_LITERAL"])
    def test_float_literals(self):
        for lit in ["3.14","3.",".5","1e10","1.5e-3","2E+4","1.0f","2.5L"]:
            with self.subTest(lit=lit): self.assertEqual(types(lit),["FLOAT_LITERAL"])
    def test_operators(self):
        self.assertEqual(types("a+++b"),["IDENTIFIER","INC","PLUS","IDENTIFIER"])
        self.assertEqual(types("<<= >>= << >> <= >="),["SHL_ASSIGN","SHR_ASSIGN","SHL","SHR","LE","GE"])
    def test_punctuators(self): self.assertEqual(types("(){}[];,"),["LPAREN","RPAREN","LBRACE","RBRACE","LBRACKET","RBRACKET","SEMICOLON","COMMA"])
    def test_comments_and_preprocessor(self):
        res,_=lex("  #include <stdio.h>\nint x;"); self.assertEqual(res["tokens"][0]["type"],"PREPROCESSOR")
        src="a // line\n/* block */ b"; self.assertEqual(types(src),["IDENTIFIER","IDENTIFIER"])
        self.assertEqual(types(src,"--comments"),["IDENTIFIER","COMMENT","COMMENT","IDENTIFIER"])
class ErrorTests(unittest.TestCase):
    def test_valid_fixture(self):
        with open(os.path.join(FIXTURES,"valid_basic.c"),"rb") as f: res,rc=lex(f.read())
        self.assertEqual(rc,0); self.assertEqual(res["diagnostics"],[])
    def test_bad_numbers(self):
        for lit in ["12abc","1.2.3","0x","09","1e","10f","0xZZ"]:
            with self.subTest(lit=lit):
                res,rc=lex(f"x = {lit};"); self.assertEqual([d["code"] for d in res["diagnostics"]],["LEX007"]); self.assertEqual(rc,1)
    def test_invalid_characters(self): self.assertEqual(codes("a @ b $ c"),["LEX001"]*2)
    def test_bad_literals(self):
        self.assertEqual(codes("c = '';"),["LEX004"]); self.assertEqual(codes("c = 'ab';"),["LEX005"])
        self.assertEqual(codes('s = "oops;'),["LEX002"])
    def test_unterminated_comment(self):
        res,rc=lex("int x;\n  /* oops\nmore\n"); self.assertEqual(res["diagnostics"][0]["code"],"LEX006"); self.assertEqual(rc,1)
    def test_invalid_fixture(self):
        with open(os.path.join(FIXTURES,"invalid_lexical.c"),"rb") as f: res,rc=lex(f.read())
        self.assertEqual(rc,1); self.assertGreaterEqual(len(res["diagnostics"]),8)
class RobustnessTests(unittest.TestCase):
    def test_empty_input(self):
        res,rc=lex(""); self.assertEqual((res["tokens"],res["diagnostics"],rc),([],[],0))
    def test_json_output(self): self.assertEqual(lex('char *s = "hello";')[0]["phase"],"lexical")
    def test_cli_usage_errors(self): self.assertEqual(subprocess.run([LEXER,"/no/such/file.c"],capture_output=True).returncode,2)
if __name__=="__main__": unittest.main()
