# Development Roadmap

Each step should finish with a successful build, passing tests, and a commit. CI status should be verified for the latest commit.

| Step | Deliverable | Status |
|---|---|---|
| 1 | Project scaffold, shared infrastructure, Flex lexer, CLI and lexer tests | Implemented |
| 2 | Initial Bison grammar, parser driver, syntax diagnostics and statement-level multi-error recovery | Implemented |
| 3 | AST construction, scoped symbol table, declarations and initial type checking | Implemented for a subset of C |
| 4 | Diagnosis engine and root-cause grouping of cascading errors | Partial: heuristic rules plus structured compiler-backed semantic hints for undeclared names and same-scope redeclarations |
| 5 | Rule-based repair candidates and re-analysis | Implemented for conservative syntax candidates; semantic changes are suggestion-only to avoid guessing programmer intent |
| 6 | Three-address intermediate code generation | Initial TAC generator implemented |
| 7 | Flask backend and JSON API | Initial API implemented; compiler validation integrated |
| 8 | Web UI with editor, diagnostics, fixes and AST visualization | Initial UI implemented; diagnosis and validated repair integrated |
| 9 | Optional AI suggestions validated by the compiler | Planned |
| 10 | Evaluation using detection, repair and false-fix metrics | Planned |
| 11 | Basic-block construction and TAC optimizations | Implemented initial local optimizer and end-to-end `compiler_pipeline.py` (`-O0`/`-O1`); global data-flow optimization remains future work |

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
- Parser recovery should synchronize at statement terminators so independent syntax faults later in a function can also be reported.
- JSON is the intended process boundary between compiler phases and the backend.
- TAC uses named temporaries and labels to make evaluation order and control flow inspectable.
- Repair candidates are never applied by the API until the real compiler accepts the candidate.
- Sanitizer-backed tests help detect memory errors.

## Current limitations

The grammar accepts a practical subset of C, not the full ISO C language. The parser builds an AST and performs an initial scope-aware semantic pass. Type inference, complete function-signature checking, pointer/array types, and full C compatibility rules remain incomplete. TAC generation is educational and does not yet resolve `break` and `continue` to loop-specific labels; some advanced C expression semantics are simplified. The Python diagnosis and repair rules are heuristics and are not substitutes for parser-aware validation. Compiler validation prevents an invalid candidate from being applied, but does not prove that a heuristic edit matches the programmer's intent.
