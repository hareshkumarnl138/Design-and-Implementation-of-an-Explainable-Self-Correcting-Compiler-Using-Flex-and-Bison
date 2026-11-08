# Explainable Self-Correcting Compiler (Flex + Bison)

**Design and Implementation of an Explainable Self-Correcting Compiler Using Flex and Bison with Intelligent Error Diagnosis and Automated Code Repair**

A compiler project for a defined subset of C. It combines a Flex lexer, Bison parser, AST construction, initial semantic analysis, three-address intermediate code generation, explainable Python diagnostics, conservative repair candidates, and compiler-backed repair validation.

> **Status:** The lexer, parser, AST, initial scoped semantic checks, and TAC output are implemented for a subset of C. The Python diagnosis/repair layer and Flask/browser interface are present. Repair candidates are now re-analyzed by the actual compiler before the API applies them. The TAC optimizer is available through an end-to-end pipeline command; broader grammar/type coverage remains future work.

## Features

- Flex lexer with source locations and lexical diagnostic codes
- Bison grammar for a practical subset of C
- Parser driver with syntax diagnostics, AST JSON output (`--ast`), TAC output (`--tac` or `--ir`), and statement-level error recovery that can report multiple malformed statements in one function
- AST nodes for declarations, functions, blocks, control flow, and expressions
- Initial semantic checks for undeclared identifiers, same-scope redeclarations, invalid function calls, return-type errors, and `break`/`continue` used outside loops
- Three-address code generation for supported expressions, assignments, calls, returns, branches, and loops
- TAC optimizer with basic-block/CFG construction, local constant folding, constant propagation, and dead temporary elimination; end-to-end `compiler_pipeline.py` supports `-O0` and `-O1`
- Explainable Python heuristic diagnosis enriched with compiler semantic findings (undeclared names and same-scope redeclarations), including typo hints only when a single declared name is the uniquely closest match; ambiguous matches are explained without guessing
- Conservative repair candidate generation
- Compiler-backed validation of repair candidates using the Flex/Bison parser and semantic pass
- Flask JSON API and browser UI
- Automated lexer, parser, diagnosis, repair-validation, and API tests

The parser is not a complete ISO C parser. TAC is an educational intermediate representation, not machine code. Some C constructs and control-flow details (including full pointer/array semantics and precise `break`/`continue` target resolution) are not yet supported. Diagnosis rules remain heuristics and can miss errors or report false positives. A repair is applied by the API only when the compiler executable is available and accepts the candidate; all changes should still be reviewed.

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
```

Read source from standard input:

```bash
echo 'int main(void) { int a = 2; int b = 3; return a + b * 4; }' | ./compiler/build/parser --tac -
```

## Run the compiler optimization pipeline

Build the compiler first:

```bash
make
```

Generate raw TAC (optimization disabled):

```bash
python3 compiler_pipeline.py tests/fixtures/valid_basic.c -O0
```

Generate optimized TAC with a basic-block/CFG summary and instruction-count report:

```bash
python3 compiler_pipeline.py tests/fixtures/valid_basic.c -O1 --blocks --report
```

- `-O0` emits the parser's original TAC.
- `-O1` applies local constant folding, constant propagation, and dead temporary elimination.
- `--blocks` prints block successors to standard error.
- `--report` prints TAC instruction counts before and after optimization to standard error.

The optimizer is currently local to each basic block; it is not a global data-flow optimizer.
## Run the diagnosis and repair API

```bash
python -m pip install -r requirements.txt
make
python backend/app.py
```

Open `http://127.0.0.1:5000`.

- `GET /api/health` — API and compiler availability
- `POST /api/diagnose` — heuristic findings plus real compiler validation
- `POST /api/repair` — generate a candidate, validate it with the compiler, and apply it only if validation succeeds

POST endpoints expect JSON with a string field named `source`.

Example:

```json
{"source":"int main(void) { return 0 }"}
```

If a candidate fails parsing or semantic analysis, the API preserves the original source and reports the compiler diagnostics.

## Repository structure

```text
.
├── compiler/       Flex lexer, Bison grammar, AST, semantic and TAC modules
├── diagnosis/      Explainable diagnosis, repair candidates and validation
├── backend/        Flask JSON API
├── frontend/       Browser UI
├── tests/          Lexer/parser/diagnosis/API tests and C fixtures
└── docs/           Roadmap, architecture, and lexer documentation
```

## Next development milestones

1. Build basic blocks and implement constant folding, propagation, and dead-code elimination over TAC.
2. Resolve loop-control targets and expand TAC coverage for more C constructs.
3. Expand parser-aware repair rules and improve source-range tracking.
4. Evaluate detection accuracy, successful repairs, and false-fix rate.

See [the roadmap](docs/ROADMAP.md) and [architecture notes](docs/architecture.md).
