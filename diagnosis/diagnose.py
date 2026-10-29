"""Explainable heuristic diagnostics for a beginner-friendly C subset."""
from __future__ import annotations
from dataclasses import asdict, dataclass
import re

@dataclass(frozen=True)
class Finding:
    code: str
    severity: str
    line: int
    column: int
    message: str
    explanation: str
    suggestion: str = ""
    def to_dict(self) -> dict:
        return asdict(self)

def _line_col(source: str, offset: int) -> tuple[int, int]:
    line = source.count("\n", 0, offset) + 1
    return line, offset - source.rfind("\n", 0, offset)

def _mask(source: str) -> str:
    pattern = re.compile(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'')
    return pattern.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), source)

def diagnose(source: str) -> list[Finding]:
    findings: list[Finding] = []
    masked = _mask(source)
    pairs = {")": "(", "]": "[", "}": "{"}
    stack: list[tuple[str, int]] = []
    for offset, char in enumerate(masked):
        if char in "([{":
            stack.append((char, offset))
        elif char in ")]}":
            if stack and stack[-1][0] == pairs[char]:
                stack.pop()
            else:
                line, col = _line_col(source, offset)
                findings.append(Finding("SYN001", "error", line, col,
                    f"Unmatched closing delimiter '{char}'.",
                    f"No matching '{pairs[char]}' was found before this delimiter.",
                    f"Add '{pairs[char]}' or remove the extra '{char}'." ))
    for opener, offset in stack:
        line, col = _line_col(source, offset)
        closer = {"(": ")", "[": "]", "{": "}"}[opener]
        findings.append(Finding("SYN002", "error", line, col,
            f"Opening delimiter '{opener}' is not closed.",
            f"The '{opener}' has no matching '{closer}'.",
            f"Insert '{closer}' at the appropriate position."))

    for index, raw in enumerate(source.splitlines()):
        stripped = raw.strip()
        clean = _mask(raw).strip()
        if not stripped or stripped.startswith(("#", "//", "/*", "*")):
            continue
        exempt = (clean.endswith((";", "{", "}", ":", ",")) or
            re.match(r"^(if|else|for|while|switch|do)\b", clean) is not None)
        likely_statement = re.match(
            r"^(return\b|break\b|continue\b|[A-Za-z_]\w*\s*=|"
            r"(?:int|float|double|char|void)\s+|printf\s*\(|scanf\s*\()", clean
        ) is not None
        if likely_statement and not exempt and not clean.endswith(";"):
            col = len(raw.rstrip()) - len(raw.rstrip().lstrip()) + len(raw.rstrip().lstrip()) + 1
            findings.append(Finding("SYN003", "warning", index + 1, col,
                "Possible missing semicolon at the end of this statement.",
                "C declarations, assignments, calls and return statements normally end with ';'.",
                "Add ';' if this is a complete statement."))

    for match in re.finditer(r"(?<![=!<>])=(?!=)", masked):
        line_start = masked.rfind("\n", 0, match.start()) + 1
        prefix = masked[line_start:match.start()]
        if re.search(r"\b(if|while)\s*\([^)]*$", prefix):
            line, col = _line_col(source, match.start())
            findings.append(Finding("SEM001", "warning", line, col,
                "Assignment appears inside a conditional expression.",
                "A single '=' assigns; '==' compares. Assignment may be intentional.",
                "If comparison was intended, replace '=' with '=='."))

    findings.sort(key=lambda f: (f.line, f.column, f.code))
    return findings
