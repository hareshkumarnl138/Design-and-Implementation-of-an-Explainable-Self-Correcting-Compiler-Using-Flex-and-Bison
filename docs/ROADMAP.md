# Development Roadmap

Each step ends with a green `make test` and a git commit.

| Step | Deliverable | Status |
|---|---|---|
| 1 | Project scaffold, shared infrastructure, Flex lexer, CLI and test suite | Done |
| 2 | Bison parser for the C subset: grammar, AST, syntax diagnostics and recovery | Next |
| 3 | Semantic analysis: scoped symbol table, declarations and type checking | Planned |
| 4 | Diagnosis engine and root-cause grouping of cascading errors | Planned |
| 5 | Rule-based repair engine with candidate edits and re-analysis | Planned |
| 6 | Intermediate code generation | Planned |
| 7 | Flask backend and JSON API | Planned |
| 8 | Web UI with editor, diagnostics, fixes and AST visualization | Planned |
| 9 | Optional AI suggestions validated by the compiler | Planned |
| 10 | Evaluation using detection, repair and false-fix metrics | Planned |

## Design decisions

- Stable diagnostic codes allow explanations and repair rules to evolve independently.
- Byte offsets make source edits precise.
- Error recovery should allow analysis to continue after a fault.
- JSON is the process boundary between compiler phases and the backend.
- Sanitizer-backed tests help detect memory errors.
