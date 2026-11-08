"""Conservative text repairs with compiler-backed candidate validation."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from pathlib import Path
import re
import subprocess

from .diagnose import diagnose
from .semantic_hints import compiler_findings

ROOT = Path(__file__).resolve().parents[1]
PARSER = ROOT / "compiler" / "build" / "parser"
VALIDATION_TIMEOUT_SECONDS = 5


def resolve_parser_path() -> Path:
    """Resolve the parser executable on POSIX and Windows/MSYS2 builds."""
    if PARSER.is_file():
        return PARSER
    windows_executable = PARSER.with_name(PARSER.name + ".exe")
    if windows_executable.is_file():
        return windows_executable
    return PARSER


@dataclass(frozen=True)
class Repair:
    rule: str
    line: int
    before: str
    after: str
    explanation: str

    def to_dict(self) -> dict:
        return asdict(self)


def validate_source(source: str) -> dict:
    """Run the real Flex/Bison compiler and semantic pass against source text."""
    parser_executable = resolve_parser_path()
    if not parser_executable.is_file():
        return {
            "available": False,
            "valid": False,
            "returncode": None,
            "stdout": "",
            "stderr": "Compiler executable not found. Run 'make' from the repository root.",
        }
    try:
        result = subprocess.run(
            [str(parser_executable), "-"],
            input=source,
            text=True,
            capture_output=True,
            cwd=ROOT,
            timeout=VALIDATION_TIMEOUT_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {
            "available": True,
            "valid": False,
            "returncode": None,
            "stdout": "",
            "stderr": "Compiler validation timed out.",
        }
    except OSError as exc:
        return {
            "available": False,
            "valid": False,
            "returncode": None,
            "stdout": "",
            "stderr": f"Could not execute compiler: {exc}",
        }
    return {
        "available": True,
        "valid": result.returncode == 0,
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def repair_source(source: str) -> tuple[str, list[Repair]]:
    """Generate conservative repair candidates; validation is a separate step."""
    lines = source.splitlines(keepends=True)
    repairs: list[Repair] = []
    output: list[str] = []
    statement = re.compile(
        r"^\s*(?:return(?:\s+[^;{}]+)?|break|continue|"
        r"(?:int|float|double|char)\s+[A-Za-z_]\w*(?:\s*=.*)?|"
        r"[A-Za-z_]\w*\s*=\s*[^=].*)\s*$"
    )
    in_block_comment = False
    for number, original in enumerate(lines, start=1):
        newline = "\n" if original.endswith("\n") else ""
        body = original[:-1] if newline else original
        stripped = body.strip()
        if in_block_comment:
            output.append(original)
            if "*/" in body:
                in_block_comment = False
            continue
        if "/*" in body and "*/" not in body:
            in_block_comment = True
            output.append(original)
            continue
        if not stripped or stripped.startswith(("//", "/*", "*", "#")):
            output.append(original)
            continue
        if (
            statement.match(body)
            and not stripped.endswith((";", "{", "}", ":", ","))
            and not re.match(r"^(if|while|for|switch|else)\b", stripped)
            and "//" not in body
            and "/*" not in body
        ):
            fixed = body + ";"
            output.append(fixed + newline)
            repairs.append(
                Repair(
                    "FIX001",
                    number,
                    body,
                    fixed,
                    "Added a semicolon to a simple statement that appeared unterminated.",
                )
            )
        else:
            output.append(original)

    candidate = "".join(output)

    # A missing closing brace is a safe candidate only when the heuristic
    # delimiter scanner identifies an unmatched opening curly brace. Append
    # one brace per unmatched opening brace; the real compiler remains the
    # authority that accepts or rejects the complete candidate.
    delimiter_findings = diagnose(candidate)
    missing_braces = [
        finding for finding in delimiter_findings
        if finding.code == "SYN002"
        and "Opening delimiter '{'" in finding.message
    ]
    if missing_braces:
        closers = "}" * len(missing_braces)
        had_trailing_newline = candidate.endswith("\n")
        insertion = ("\n" if candidate and not had_trailing_newline else "") + closers
        repaired = candidate + insertion
        repairs.append(
            Repair(
                "FIX002",
                candidate.count("\n") + 1,
                "",
                closers,
                "Inserted closing brace(s) for unmatched opening block delimiter(s).",
            )
        )
        candidate = repaired

    # Propose a spelling correction only when exactly one declared identifier
    # is the uniquely closest match. The full candidate is validated by the
    # compiler in the API before it can ever be applied.
    if not repairs:
        initial_validation = validate_source(candidate)
        if initial_validation["available"] and not initial_validation["valid"]:
            semantic = compiler_findings(candidate, initial_validation["stderr"])
            undeclared = [
                finding for finding in semantic if finding.code == "SEM002"
            ]
            if len(undeclared) == 1:
                finding = undeclared[0]
                # Finding.message is presentation text and starts with
                # "Undeclared" (capital U); match case-insensitively so the
                # compiler-derived typo candidate is not silently skipped.
                unknown = re.search(
                    r"undeclared identifier '([^']+)'",
                    finding.message,
                    flags=re.IGNORECASE,
                )
                declared = list(dict.fromkeys(re.findall(
                    r"\b(?:int|float|double|char)\s+([A-Za-z_]\w*)",
                    candidate,
                )))
                if unknown:
                    old_name = unknown.group(1)

                    def edit_distance(left: str, right: str) -> int:
                        previous = list(range(len(right) + 1))
                        for i, left_char in enumerate(left, 1):
                            current = [i]
                            for j, right_char in enumerate(right, 1):
                                current.append(min(
                                    current[-1] + 1,
                                    previous[j] + 1,
                                    previous[j - 1] + (left_char != right_char),
                                ))
                            previous = current
                        return previous[-1]

                    ranked = sorted(
                        ((edit_distance(old_name, name), name)
                         for name in declared if name != old_name),
                        key=lambda item: (item[0], item[1]),
                    )
                    threshold = max(2, len(old_name) // 3)
                    if (ranked and ranked[0][0] <= threshold
                            and (len(ranked) == 1 or ranked[0][0] < ranked[1][0])):
                        new_name = ranked[0][1]
                        source_lines = candidate.splitlines(keepends=True)
                        if 1 <= finding.line <= len(source_lines):
                            line_text = source_lines[finding.line - 1]
                            occurrences = list(re.finditer(
                                rf"\b{re.escape(old_name)}\b", line_text
                            ))
                            if occurrences:
                                target = min(
                                    occurrences,
                                    key=lambda item: abs(
                                        item.start() - (finding.column - 1)
                                    ),
                                )
                                start_pos, end_pos = target.span()
                                source_lines[finding.line - 1] = (
                                    line_text[:start_pos] + new_name
                                    + line_text[end_pos:]
                                )
                                candidate = "".join(source_lines)
                                repairs.append(Repair(
                                    "FIX003", finding.line, old_name, new_name,
                                    "Corrected a uniquely closest identifier spelling; "
                                    "the complete program must pass compiler validation."
                                ))

    before = sum(f.severity == "error" for f in diagnose(source))
    after = sum(f.severity == "error" for f in diagnose(candidate))
    return (source, []) if after > before else (candidate, repairs)
