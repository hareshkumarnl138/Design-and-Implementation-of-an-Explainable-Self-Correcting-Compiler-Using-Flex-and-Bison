# Explainable Self-Correcting Compiler (Flex + Bison)

**Design and Implementation of an Explainable Self-Correcting Compiler Using Flex and Bison with Intelligent Error Diagnosis and Automated Code Repair**

A compiler project for a defined subset of C. It combines a Flex lexer, an initial Bison syntax parser, explainable diagnostic rules, and conservative repair suggestions.

> **Status:** Lexer and initial parser source, Python diagnosis/repair rules, a Flask API, and a browser UI are in the repository. CI/build results should be checked before claiming these components pass. The parser now builds an AST and performs an initial scoped symbol/type analysis. Intermediate code generation, optimization, and compiler-validated repair remain future milestones.

## Features currently present in source

- Flex lexer with source locations and lexical diagnostic codes
- C token definitions and JSON output support
- Bison grammar for a practical subset of C
- Parser driver with syntax diagnostic reporting, AST JSON output (`--ast`), and basic semicolon recovery
- AST nodes for declarations, functions, blocks, control flow, and expressions
- Initial semantic checks for undeclared identifiers, same-scope redeclarations, and invalid function calls
- Python heuristic diagnosis and conservative semicolon repair
- Flask JSON API and browser UI
- Lexer and parser fixtures/unit tests
- GitHub Actions workflow for automated build and tests

The parser is not a complete ISO C parser. Diagnosis and repair rules are heuristics, can miss errors or report false positives, and must be reviewed. A repair should not be treated as valid until it passes parser and semantic checks.

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

Run syntax analysis:

```bash
./compiler/build/parser tests/fixtures/valid_basic.c
./compiler/build/parser --ast tests/fixtures/valid_basic.c
echo 'int main(void) { int value = 4 return value; }' | ./compiler/build/parser -
```

The second example should be rejected for a syntax error.

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
├── compiler/       Flex lexer, Bison grammar, drivers, shared C modules
├── diagnosis/      Explainable heuristic diagnosis and conservative repair
├── backend/        Flask JSON API
├── frontend/       Browser interface
├── tests/          Lexer/parser tests and C fixtures
└── docs/           Roadmap, architecture, and lexer documentation
```

## Next development milestones

1. Expand semantic checking for function signatures, return types, arrays, and operator compatibility.
2. Add three-address intermediate code generation from the AST.
3. Add basic-block and peephole optimizations.
4. Connect repair candidates to parser re-analysis and semantic validation.
5. Evaluate detection accuracy, successful repairs, and false-fix rate.

See [the roadmap](docs/ROADMAP.md) and [architecture notes](docs/architecture.md).
