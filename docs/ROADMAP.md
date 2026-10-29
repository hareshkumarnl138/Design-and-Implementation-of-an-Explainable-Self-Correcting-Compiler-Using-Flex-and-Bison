# Development Roadmap

Each step should finish with a successful build, passing tests, and a commit. Status reflects code added; build/test status must be checked in CI.

| Step | Deliverable | Status |
|---|---|---|
| 1 | Project scaffold, shared infrastructure, Flex lexer, CLI and lexer tests | Implemented; CI verification pending |
| 2 | Initial Bison grammar, parser driver, syntax diagnostics and recovery | Implemented; CI verification pending |
| 3 | AST construction, scoped symbol table, declarations and initial type checking | Implemented in initial form; CI verification pending |
| 4 | Diagnosis engine and root-cause grouping of cascading errors | Partial: Python heuristic rules exist |
| 5 | Rule-based repair candidates and re-analysis | Partial: conservative semicolon repair exists |
| 6 | Intermediate code generation | Planned |
| 7 | Flask backend and JSON API | Initial API implemented |
| 8 | Web UI with editor, diagnostics, fixes and AST visualization | Initial UI implemented; integration needs verification |
| 9 | Optional AI suggestions validated by the compiler | Planned |
| 10 | Evaluation using detection, repair and false-fix metrics | Planned |

## Build and test

From the repository root:

```bash
make
make test
```

The compiler subproject builds the standalone lexer and the parser:

```bash
./compiler/build/lexer tests/fixtures/valid_basic.c
./compiler/build/parser tests/fixtures/valid_basic.c
```

## Design decisions

- The lexer and parser share numeric token IDs.
- Byte offsets and source locations are retained for diagnostic reporting.
- Parser recovery should allow analysis to continue after a syntax fault.
- JSON is the intended process boundary between compiler phases and the backend.
- Sanitizer-backed tests help detect memory errors.

## Current limitations

The grammar accepts a practical subset of C, not the full ISO C language. The parser builds an AST and performs an initial scope-aware semantic pass. Type inference, function-signature checking, return-type validation, pointer/array types, and full C compatibility rules remain incomplete. The Python diagnosis and repair rules are heuristics and are not substitutes for parser-aware validation. Do not describe the complete self-correcting compiler as finished until the remaining stages and tests are implemented.
