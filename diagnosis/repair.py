"""Conservative text repairs with an explanation for each edit."""
from __future__ import annotations
from dataclasses import asdict, dataclass
import re
from .diagnose import diagnose

@dataclass(frozen=True)
class Repair:
    rule: str
    line: int
    before: str
    after: str
    explanation: str
    def to_dict(self) -> dict:
        return asdict(self)

def repair_source(source: str) -> tuple[str, list[Repair]]:
    lines = source.splitlines(keepends=True)
    repairs: list[Repair] = []
    output: list[str] = []
    statement = re.compile(r"^\s*(?:return(?:\s+[^;{}]+)?|break|continue|"
        r"(?:int|float|double|char)\s+[A-Za-z_]\w*(?:\s*=.*)?|"
        r"[A-Za-z_]\w*\s*=\s*[^=].*)\s*$")
    in_block_comment = False
    for number, original in enumerate(lines, start=1):
        newline = "\n" if original.endswith("\n") else ""
        body = original[:-1] if newline else original
        stripped = body.strip()
        if in_block_comment:
            output.append(original)
            if "*/" in body: in_block_comment = False
            continue
        if "/*" in body and "*/" not in body:
            in_block_comment = True
            output.append(original)
            continue
        if not stripped or stripped.startswith(("//", "/*", "*", "#")):
            output.append(original)
            continue
        if (statement.match(body) and not stripped.endswith((";", "{", "}", ":", ","))
            and not re.match(r"^(if|while|for|switch|else)\b", stripped)
            and "//" not in body and "/*" not in body):
            fixed = body + ";"
            output.append(fixed + newline)
            repairs.append(Repair("FIX001", number, body, fixed,
                "Added a semicolon to a simple statement that appeared unterminated."))
        else:
            output.append(original)
    candidate = "".join(output)
    before = sum(f.severity == "error" for f in diagnose(source))
    after = sum(f.severity == "error" for f in diagnose(candidate))
    return (source, []) if after > before else (candidate, repairs)
