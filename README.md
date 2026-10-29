# Explainable Self-Correcting Compiler (Flex + Bison)

**Design and Implementation of an Explainable Self-Correcting Compiler Using Flex and Bison with Intelligent Error Diagnosis and Automated Code Repair**

A compiler front-end for a defined subset of C that detects lexical errors, explains their causes, and is designed to grow into a self-correcting compiler.

> **Project status:** Step 1 of the roadmap is the Flex lexer. The Bison parser, semantic analysis, diagnosis/repair engine, backend, and frontend remain planned. See [docs/ROADMAP.md](docs/ROADMAP.md).

## Implemented in the current source

- Flex lexer for a defined C subset
- Source locations: line, column, byte offset, and length
- Lexical error codes and recovery
- Shared diagnostic collector and JSON output contract
- Command-line lexer with readable and JSON output
- Test fixtures and Python tests

## Planned

Bison parser, semantic analysis, explainable error diagnosis, rule-based repair, intermediate code, Flask backend, web UI, optional AI suggestions, and evaluation.

## Getting started

On Debian/Ubuntu, install the required tools:

```bash
sudo apt update
sudo apt install build-essential flex bison make python3
```

Build the lexer:

```bash
make
```

Run the test suite:

```bash
make test
```

Try the lexer:

```bash
./compiler/build/lexer tests/fixtures/invalid_lexical.c
./compiler/build/lexer --json tests/fixtures/valid_basic.c
echo 'int x = 5 @ 3;' | ./compiler/build/lexer -
```

## Repository structure

```text
.
├── compiler/       Flex lexer, shared C modules, and Makefile
├── diagnosis/      Planned diagnosis and repair rules
├── backend/        Planned Flask API
├── frontend/       Planned web interface
├── tests/          Python tests and C fixtures
└── docs/           Roadmap and lexical-analysis documentation
```

## Safety and repair policy

Proposed changes should be shown for review before being applied. Ambiguous fixes should remain suggestions rather than being applied silently. Optional AI-generated suggestions must be independently validated by compiler checks.

## Documentation

- [Roadmap and design decisions](docs/ROADMAP.md)
- [Lexical analysis: usage, token categories, diagnostics](docs/lexer.md)
