"""Conservative text repairs with compiler-backed candidate validation."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from pathlib import Path
import re
import subprocess

from .diagnose import diagnose

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
        r"^\\s*(?:return(?:\\s+[^;{}]+)?|break|continue|"
        r"(?:int|float|double|char)\\s+[A-Za-z_]\\w*(?:\\s*=.*)?|"
        r"[A-Za-z_]\\w*\\s*=\\s*[^=].*)\\s*$"
    )
    in_block_comment = False
    for number, original in enumerate(lines, start=1):
        newline = "\\n" if original.endswith("\\n") else ""
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
            and not re.match(r"^(if|while|for|switch|else)\\b", stripped)
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
    before = sum(f.severity == "error" for f in diagnose(source))
    after = sum(f.severity == "error" for f in diagnose(candidate))
    return (source, []) if after > before else (candidate, repairs)
