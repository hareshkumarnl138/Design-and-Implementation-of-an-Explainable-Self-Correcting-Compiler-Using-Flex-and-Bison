# Explainable Self-Correcting Compiler (Flex + Bison)

**Design and Implementation of an Explainable Self-Correcting Compiler Using Flex and Bison with Intelligent Error Diagnosis and Automated Code Repair**

A compiler project for a defined subset of C. It combines a Flex lexer, a Bison parser, explainable diagnostic rules, conservative repair suggestions, AST construction, initial semantic analysis, and three-address intermediate code generation.

> **Status:** The lexer, parser, AST, initial scoped symbol/type checks, and TAC output are implemented for a subset of C. Python diagnosis/repair rules, a Flask API, and a browser UI are also present. CI should be checked for the latest commit before claiming the complete project is production-ready. Optimizations and compiler-validated repair remain future milestones.

## Features currently present in source

- Flex lexer with source locations and lexical diagnostic codes
- C token definitions and JSON output support
- Bison grammar for a practical subset of C
- Parser driver with syntax diagnostics, AST JSON output (`--ast`), TAC output (`--tac` or `--ir`), and basic semicolon recovery
- AST nodes for declarations, functions, blocks, control flow, and expressions
- Initial semantic checks for undeclared identifiers, same-scope redeclarations, invalid function calls, and some return-type errors
- Three-address code generation for arithmetic/logical expressions, assignments, function calls, returns, branches, and loop structures
- Python heuristic diagnosis and conservative semicolon repair
- Flask JSON API and browser UI
- Lexer and parser fixtures/unit tests
- GitHub Actions workflow for automated build and tests

The parser is not a complete ISO C parser. TAC is an educational intermediate representation, not machine code. Some C constructs and control-flow details (including full pointer/array semantics and precise break/continue target resolution) are not yet supported. Diagnosis and repair rules are heuristics, can miss errors or report false positives, and must be reviewed. A repair should not be treated as valid until it passes parser and semantic checks.

## Requirements

On Debian/Ubuntu:

```bash
sudo apt update
sudo apt install build-essential flex bison make python3 python3-pip
python -m pip install -r requirements.txt
```

## Build and test

From the repository root:

```bash
make
make test
```

Run lexical analysis:

```bash
./compiler/build/lexer tests/fixtures/valid_basic.c
./compiler/build/lexer --json tests/fixtures/invalid_lexical.c
```

Run syntax analysis and AST generation:

```bash
./compiler/build/parser tests/fixtures/valid_basic.c
./compiler/build/parser --ast tests/fixtures/valid_basic.c
```

Generate three-address code:

```bash
./compiler/build/parser --tac tests/fixtures/valid_basic.c
# --ir is an alias for --tac
```

Read source from standard input:

```bash
echo 'int main(void) { int a = 2; int b = 3; return a + b * 4; }' | ./compiler/build/parser --tac -
```

The following syntax example should be rejected:

```bash
echo 'int main(void) { int value = 4 return value; }' | ./compiler/build/parser -
```

## Run the diagnosis API

```bash
python -m pip install -r requirements.txt
python backend/app.py
```

Open `http://127.0.0.1:5000`. API endpoints:

- `GET /api/health`
- `POST /api/diagnose`
- `POST /api/repair`

POST endpoints expect JSON with a string field named `source`.

## Repository structure

```text
.
├── compiler/       Flex lexer, Bison grammar, AST, semantic and TAC modules
├── diagnosis/      Explainable heuristic diagnosis and conservative repair
├── backend/        Flask JSON API
├── frontend/       Browser UI
├── tests/          Lexer/parser tests and C fixtures
└── docs/           Roadmap, architecture, and lexer documentation
```

## Next development milestones

1. Add basic-block construction and peephole/constant-folding optimizations over TAC.
2. Resolve loop-control targets and expand TAC coverage for more C constructs.
3. Connect repair candidates to parser re-analysis and semantic validation.
4. Evaluate detection accuracy, successful repairs, and false-fix rate.

See [the roadmap](docs/ROADMAP.md) and [architecture notes](docs/architecture.md).
