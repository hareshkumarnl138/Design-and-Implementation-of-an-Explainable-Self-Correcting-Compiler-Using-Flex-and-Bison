"""End-to-end C-to-TAC pipeline with optional TAC optimization.

Run from the repository root:
    python3 compiler_pipeline.py source.c -O0
    python3 compiler_pipeline.py source.c -O1 --blocks --report
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from compiler.tac_optimizer import optimize_tac

ROOT = Path(__file__).resolve().parent
DEFAULT_COMPILER = ROOT / "compiler" / "build" / "parser"


def resolve_compiler_path(compiler: Path) -> Path:
    """Resolve GCC/MSYS2 executable names on Windows, where binaries use .exe."""
    if compiler.is_file():
        return compiler
    if compiler.suffix.lower() != ".exe":
        windows_executable = compiler.with_name(compiler.name + ".exe")
        if windows_executable.is_file():
            return windows_executable
    return compiler


def compile_to_tac(source: str, compiler: Path) -> str:
    """Run the Flex/Bison compiler and return TAC, raising on compiler errors."""
    compiler = resolve_compiler_path(compiler)
    if not compiler.is_file():
        raise FileNotFoundError(
            f"Compiler executable not found: {compiler}. Build it first with 'make'."
        )
    result = subprocess.run(
        [str(compiler), "--tac", source],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        timeout=15,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "Compilation failed."
        raise RuntimeError(detail)
    return result.stdout


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", help="C source file to compile")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("-O0", dest="optimization", action="store_const", const=0,
                      help="emit raw TAC without optimization (default)")
    mode.add_argument("-O1", dest="optimization", action="store_const", const=1,
                      help="apply local TAC optimizations")
    parser.set_defaults(optimization=0)
    parser.add_argument("--compiler", type=Path, default=DEFAULT_COMPILER,
                        help="path to the compiled Flex/Bison parser")
    parser.add_argument("--blocks", action="store_true",
                        help="print basic blocks and CFG successors (with -O1)")
    parser.add_argument("--report", action="store_true",
                        help="print before/after TAC instruction counts (with -O1)")
    args = parser.parse_args(argv)

    try:
        raw = compile_to_tac(args.source, args.compiler)
        if args.optimization == 0:
            sys.stdout.write(raw)
            if args.blocks or args.report:
                print("Note: --blocks and --report require -O1; no optimization was run.",
                      file=sys.stderr)
            return 0

        optimized, blocks = optimize_tac(raw)
        sys.stdout.write(optimized)
        if args.blocks:
            print("\\nBasic blocks and CFG successors:", file=sys.stderr)
            for block in blocks:
                print(f"  {block.name}: {', '.join(block.successors) or '(exit)'}",
                      file=sys.stderr)
        if args.report:
            before = sum(bool(line.strip()) and not line.lstrip().startswith("#")
                         for line in raw.splitlines())
            after = sum(bool(line.strip()) and not line.lstrip().startswith("#")
                        for line in optimized.splitlines())
            print(f"TAC instructions: {before} -> {after} "
                  f"(removed {before - after})", file=sys.stderr)
        return 0
    except (OSError, RuntimeError, subprocess.TimeoutExpired) as exc:
        print(f"compiler pipeline: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
