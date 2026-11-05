"""Turn compiler semantic diagnostics into actionable, explainable hints."""
from __future__ import annotations

import re

from .diagnose import Finding

_COMPILER_ERROR = re.compile(
    r"^-:(\d+):(\d+):\s+error\[(SEM\d+)\]:\s+(.*)$"
)
_DECLARATION = re.compile(
    r"\b(?:int|float|double|char|void)\s+([A-Za-z_]\w*)"
)


def _distance(left: str, right: str) -> int:
    """Small Levenshtein distance implementation; no third-party dependency."""
    previous = list(range(len(right) + 1))
    for i, a in enumerate(left, 1):
        current = [i]
        for j, b in enumerate(right, 1):
            current.append(min(
                current[-1] + 1,
                previous[j] + 1,
                previous[j - 1] + (a != b),
            ))
        previous = current
    return previous[-1]


def compiler_findings(source: str, stderr: str) -> list[Finding]:
    """Convert SEM001/SEM002 compiler errors to structured UI findings."""
    declared = list(dict.fromkeys(_DECLARATION.findall(source)))
    findings: list[Finding] = []
    for raw in stderr.splitlines():
        match = _COMPILER_ERROR.match(raw.strip())
        if not match:
            continue
        line, column, code, message = match.groups()
        line_number, column_number = int(line), int(column)
        if code == "SEM002":
            unknown = re.search(r"undeclared identifier '([^']+)'", message)
            name = unknown.group(1) if unknown else ""
            ranked = sorted(
                ((_distance(name, item), item) for item in declared if item != name),
                key=lambda item: (item[0], item[1]),
            )
            suggestion = ""
            if ranked and ranked[0][0] <= max(1, len(name) // 3):
                suggestion = (
                    f"Did you mean '{ranked[0][1]}'? Check the spelling and scope; "
                    "the compiler will not rename it automatically."
                )
            else:
                suggestion = (
                    "Declare the identifier in the correct scope or use the intended "
                    "existing variable. No automatic rename was applied."
                )
            findings.append(Finding(
                code, "error", line_number, column_number,
                f"Undeclared identifier '{name}'.",
                "This name is used, but no visible declaration was found at this point.",
                suggestion,
            ))
        elif code == "SEM001":
            redeclared = re.search(r"Redeclaration of '([^']+)'", message)
            name = redeclared.group(1) if redeclared else "identifier"
            findings.append(Finding(
                code, "error", line_number, column_number,
                f"'{name}' is declared more than once in the same scope.",
                "The compiler found an earlier declaration with the same name in this scope.",
                "Rename one declaration if these are different variables, or remove the "
                "duplicate if it was accidental. No automatic change was applied.",
            ))
    return findings
