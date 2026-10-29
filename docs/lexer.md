# Lexical Analysis (Step 1)

Source: `compiler/lexer.l`. Binary: `compiler/build/lexer`.

## Usage

```bash
lexer [--json] [--comments] [FILE | -]
```

| Flag | Effect |
|---|---|
| `--json` | Machine-readable output |
| `--comments` | Emit comments as COMMENT tokens |
| `-` | Read from stdin |

Exit status: 0 means no lexical errors, 1 means lexical errors, and 2 means usage or I/O error.

## Supported token categories

- Keywords: int, float, double, char, void, if, else, while, for, do, return, break, continue
- Literals: integer, floating-point, character and string
- Operators: arithmetic, assignment, comparison, logical and bitwise
- Punctuators: parentheses, braces, brackets, semicolon and comma
- Trivia: preprocessor lines and comments

## Diagnostics

| Code | Meaning |
|---|---|
| LEX001 | Invalid character |
| LEX002 | Unterminated string literal |
| LEX003 | Unterminated character literal |
| LEX004 | Empty character literal |
| LEX005 | Multi-character constant |
| LEX006 | Unterminated block comment |
| LEX007 | Malformed numeric literal |
| LEX008 | Unknown escape sequence (warning) |

## JSON contract

Output includes phase, file, tokens, diagnostics and a summary. Each token includes line, column, byte offset, length and error status. Byte offsets allow later repair modules to refer to exact source spans.
