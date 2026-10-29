# Architecture

The project has three layers:

1. **C lexer** (`compiler/`) — Flex-based tokenization and lexical diagnostics for the documented C subset.
2. **Python diagnosis and repair** (`diagnosis/`) — explainable rules for delimiter mismatches, likely missing semicolons, and assignment inside conditions.
3. **HTTP API and UI** (`backend/app.py`, `frontend/index.html`) — JSON endpoints for diagnosis and repair suggestions.

## Inspect the AST and run semantic checks\n\nBuild the compiler with `make`. Run `./compiler/build/parser --ast path/to/file.c` to print the parsed AST as JSON. Run `./compiler/build/parser path/to/file.c` to parse and perform the initial semantic pass.\n\n## Run the API

```bash
python -m pip install -r requirements.txt
python backend/app.py
```

Endpoints:
- `GET /api/health`
- `POST /api/diagnose` with JSON body `{"source":"int main() { return 0; }"}`
- `POST /api/repair` with the same body shape

The Python rules are heuristics, not a complete C parser or semantic analyzer. They can miss errors or report false positives, especially for macros, multiline statements, and complex declarations. Review all automatic edits and compile the result before use. The Bison parser builds an AST (`compiler/ast.c`) and the initial semantic analyzer (`compiler/semantic.c`) uses nested scopes to detect undeclared identifiers and same-scope redeclarations. It also emits warnings where expression or external-function types cannot be verified. This is an initial subset-oriented semantic pass, not a complete C type checker.
