# Development Roadmap

Each step should finish with a successful build, passing tests, and a commit. CI status should be verified for the latest commit.

| Step | Deliverable | Status |
|---|---|---|
| 1 | Project scaffold, shared infrastructure, Flex lexer, CLI and lexer tests | Implemented |
| 2 | Initial Bison grammar, parser driver, syntax diagnostics and recovery | Implemented |
| 3 | AST construction, scoped symbol table, declarations and initial type checking | Implemented for a subset of C |
| 4 | Diagnosis engine and root-cause grouping of cascading errors | Partial: Python heuristic rules exist |
| 5 | Rule-based repair candidates and re-analysis | Partial: conservative semicolon repair exists |
| 6 | Three-address intermediate code generation | Initial TAC generator implemented |
| 7 | Flask backend and JSON API | Initial API implemented |
| 8 | Web UI with editor, diagnostics, fixes and AST visualization | Initial UI implemented; integration needs verification |
| 9 | Optional AI suggestions validated by the compiler | Planned |
| 10 | Evaluation using detection, repair and false-fix metrics | Planned |
| 11 | Basic-block construction and TAC optimizations | Planned |

## Build and test

From the repository root:

```bash
make
make test
```

The compiler subproject builds the standalone lexer and parser:

```bash
./compiler/build/lexer tests/fixtures/valid_basic.c
./compiler/build/parser tests/fixtures/valid_basic.c
./compiler/build/parser --ast tests/fixtures/valid_basic.c
./compiler/build/parser --tac tests/fixtures/valid_basic.c
```

## Design decisions

- The lexer and parser share numeric token IDs.
- Byte offsets and source locations are retained for diagnostic reporting.
- Parser recovery should allow analysis to continue after a syntax fault.
- JSON is the intended process boundary between compiler phases and the backend.
- TAC uses named temporaries and labels to make evaluation order and control flow inspectable.
- Sanitizer-backed tests help detect memory errors.

## Current limitations

The grammar accepts a practical subset of C, not the full ISO C language. The parser builds an AST and performs an initial scope-aware semantic pass. Type inference, complete function-signature checking, pointer/array types, and full C compatibility rules remain incomplete. TAC generation is educational and does not yet resolve `break` and `continue` to loop-specific labels; some advanced C expression semantics are simplified. The Python diagnosis and repair rules are heuristics and are not substitutes for parser-aware validation. Do not describe the complete self-correcting compiler as finished until the remaining stages and tests are implemented.
