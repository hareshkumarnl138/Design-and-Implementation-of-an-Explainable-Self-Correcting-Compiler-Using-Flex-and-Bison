# Architecture

The project has three layers:

1. **C lexer** (`compiler/`) — Flex-based tokenization and lexical diagnostics for the documented C subset.
2. **Python diagnosis and repair** (`diagnosis/`) — explainable rules for delimiter mismatches, likely missing semicolons, and assignment inside conditions.
3. **HTTP API and UI** (`backend/app.py`, `frontend/index.html`) — JSON endpoints for diagnosis and repair suggestions.

## Run the API

```bash
python -m pip install -r requirements.txt
python backend/app.py
```

Endpoints:
- `GET /api/health`
- `POST /api/diagnose` with JSON body `{"source":"int main() { return 0; }"}`
- `POST /api/repair` with the same body shape

The Python rules are heuristics, not a complete C parser or semantic analyzer. They can miss errors or report false positives, especially for macros, multiline statements, and complex declarations. Review all automatic edits and compile the result before use. The Bison parser, AST, symbol table and semantic type checker remain future compiler milestones.
