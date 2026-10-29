# Explainable Self-Correcting Compiler (Flex + Bison)

**Design and Implementation of an Explainable Self-Correcting Compiler Using Flex and Bison with Intelligent Error Diagnosis and Automated Code Repair**

A compiler project for a defined subset of C, combining a Flex lexer with explainable source diagnostics and conservative repair suggestions.

> **Project status:** The Flex lexer and an initial Python diagnosis/repair API are present. The full Bison parser, AST, symbol table, semantic/type analysis, and complete compiler pipeline are not implemented yet. Check [the roadmap](docs/ROADMAP.md) for remaining milestones.

## Implemented components

- Flex lexer with source locations and lexical diagnostic codes
- Shared C diagnostic collector and JSON output support
- Command-line lexer and token definitions
- Python heuristics for unmatched delimiters, likely missing semicolons, and suspicious assignment in conditions
- Conservative semicolon repair for selected simple statements, with a record explaining each edit
- Flask JSON API and lightweight browser interface
- Python unit tests and C fixture programs

The diagnosis and repair rules are **heuristics**, not a complete C parser. They can produce false positives or miss errors. Review every proposed edit and compile the result before using it.

## Requirements

For the C lexer on Debian/Ubuntu:

```bash
sudo apt update
sudo apt install build-essential flex bison make python3
```

For the Python API:

```python
python -m pip install -r requirements.txt
```

## Build and test the lexer

```bash
make
make test
```

Try the lexer:

```bash
./compiler/build/lexer tests/fixtures/invalid_lexical.c
./compiler/build/lexer --json tests/fixtures/valid_basic.c
echo 'int x = 5 @ 3;' | ./compiler/build/lexer -
```

## Run the diagnosis API

From the repository root:

```bash
python backend/app.py
```

API endpoints:

- `GET http://127.0.0.1:5000/api/health`
- `POST http://127.0.0.1:5000/api/diagnose`
- `POST http://127.0.0.1:5000/api/repair`

POST endpoints expect JSON with a string field named `source`. Example:

```bash
curl -X POST http://127.0.0.1:5000/api/diagnose \
  -H "Content-Type: application/json" \
  -d '{"source":"int main() { return 0; }"}'
```

The browser interface is in `frontend/index.html`. It calls the API on the same origin, so serve it through a web server that proxies `/api` to Flask, or configure your local development server accordingly.

## Repository structure

```text
.
├── compiler/       Flex lexer and shared C modules
├── diagnosis/      Explainable diagnosis and conservative repair rules
├── backend/        Flask JSON API
├── frontend/       Browser interface
├── tests/          Python tests and C fixtures
└── docs/           Roadmap, architecture, and lexer documentation
```

## Roadmap

The next major compiler milestones are the Bison grammar/parser, AST construction, symbol-table and semantic analysis, parser-aware error recovery, repair validation through recompilation, and end-to-end integration. Optional AI-generated suggestions should be independently validated by compiler checks.

## Documentation

- [Roadmap](docs/ROADMAP.md)
- [Architecture](docs/architecture.md)
- [Lexer documentation](docs/lexer.md)
- [Backend API notes](backend/README.md)
