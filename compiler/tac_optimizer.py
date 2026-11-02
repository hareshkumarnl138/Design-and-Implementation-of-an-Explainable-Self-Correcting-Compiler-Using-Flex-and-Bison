"""Basic-block construction and conservative optimization for textual TAC."""
from __future__ import annotations
import argparse
import re
from dataclasses import dataclass, field
from pathlib import Path

LABEL = re.compile(r"^(L[\w]*):$")
BRANCH = re.compile(r"^(?:if(?:False)?\s+.+\s+goto|goto)\s+(L[\w]*)$")
ASSIGN = re.compile(r"^([A-Za-z_]\w*)\s*=\s*(.+)$")
BINARY = re.compile(r"^([A-Za-z_]\w*|-?\d+(?:\.\d+)?)\s*([+\-*\/%])\s*([A-Za-z_]\w*|-?\d+(?:\.\d+)?)$")
NUMBER = re.compile(r"^-?(?:\d+(?:\.\d*)?|\.\d+)$")
IDENT = re.compile(r"\b[A-Za-z_]\w*\b")


@dataclass
class BasicBlock:
    name: str
    instructions: list[str] = field(default_factory=list)
    successors: list[str] = field(default_factory=list)


def _is_terminator(line: str) -> bool:
    return line.startswith(("goto ", "if ", "ifFalse ", "return"))


def build_basic_blocks(lines: list[str]) -> list[BasicBlock]:
    """Split TAC at labels and after control-flow terminators."""
    leaders = {0}
    for i, raw in enumerate(lines):
        line = raw.strip()
        if not line:
            continue
        if LABEL.match(line):
            leaders.add(i)
        if _is_terminator(line) and i + 1 < len(lines):
            leaders.add(i + 1)
    starts = sorted(leaders)
    blocks: list[BasicBlock] = []
    for n, start in enumerate(starts):
        end = starts[n + 1] if n + 1 < len(starts) else len(lines)
        chunk = [x.strip() for x in lines[start:end] if x.strip()]
        if not chunk:
            continue
        label = LABEL.match(chunk[0])
        name = label.group(1) if label else f"B{len(blocks) + 1}"
        blocks.append(BasicBlock(name, chunk))
    label_to_block = {b.name: b.name for b in blocks if LABEL.match(b.instructions[0])}
    for i, block in enumerate(blocks):
        last = block.instructions[-1]
        branch = BRANCH.match(last)
        if branch:
            target = label_to_block.get(branch.group(1))
            if target:
                block.successors.append(target)
            if last.startswith(("if ", "ifFalse ")) and i + 1 < len(blocks):
                block.successors.append(blocks[i + 1].name)
        elif not last.startswith("return") and i + 1 < len(blocks):
            block.successors.append(blocks[i + 1].name)
    return blocks


def _value(token: str, constants: dict[str, str]) -> str:
    return constants.get(token, token)


def _fold(left: str, op: str, right: str) -> str | None:
    if not NUMBER.match(left) or not NUMBER.match(right):
        return None
    a, b = float(left), float(right)
    try:
        value = {"+": lambda: a + b, "-": lambda: a - b,
                 "*": lambda: a * b, "/": lambda: a / b,
                 "%": lambda: a % b}[op]()
    except (ZeroDivisionError, KeyError):
        return None
    if value.is_integer():
        return str(int(value))
    return format(value, ".12g")


def _uses(line: str) -> set[str]:
    assigned = ASSIGN.match(line)
    rhs = assigned.group(2) if assigned else line
    return {name for name in IDENT.findall(rhs) if not name.startswith("L")}


def optimize_block(block: BasicBlock) -> BasicBlock:
    """Apply local constant propagation/folding and dead temporary removal."""
    constants: dict[str, str] = {}
    optimized: list[str] = []
    for line in block.instructions:
        if LABEL.match(line) or line.startswith("#") or line.startswith(("function ", "end function")):
            optimized.append(line)
            continue
        match = ASSIGN.match(line)
        if not match:
            optimized.append(line)
            continue
        target, rhs = match.groups()
        binary = BINARY.match(rhs)
        if binary:
            left, op, right = binary.groups()
            left, right = _value(left, constants), _value(right, constants)
            folded = _fold(left, op, right)
            rhs = folded if folded is not None else f"{left} {op} {right}"
        elif IDENT.fullmatch(rhs):
            rhs = _value(rhs, constants)
        else:
            rhs = IDENT.sub(lambda m: _value(m.group(0), constants), rhs)
        if NUMBER.match(rhs):
            constants[target] = rhs
        else:
            constants.pop(target, None)
        optimized.append(f"{target} = {rhs}")

    # Keep observable assignments; remove only unused compiler temporaries.
    live: set[str] = set()
    kept: list[str] = []
    for line in reversed(optimized):
        match = ASSIGN.match(line)
        if match and match.group(1).startswith("t"):
            target, rhs = match.groups()
            if target not in live:
                continue
            live.discard(target)
            live.update(_uses(rhs))
        else:
            live.update(_uses(line))
        kept.append(line)
    block.instructions = list(reversed(kept))
    return block


def optimize_tac(text: str) -> tuple[str, list[BasicBlock]]:
    lines = text.splitlines()
    header = [line for line in lines if line.startswith("#")]
    body = [line for line in lines if line.strip() and not line.startswith("#")]
    blocks = [optimize_block(b) for b in build_basic_blocks(body)]
    rendered = header + [line for block in blocks for line in block.instructions]
    return "\n".join(rendered) + ("\n" if rendered else ""), blocks


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="TAC text file, or - for stdin")
    parser.add_argument("-o", "--output", help="write optimized TAC to this file")
    parser.add_argument("--blocks", action="store_true", help="print basic-block and CFG summary")
    args = parser.parse_args()
    import sys
    source = sys.stdin.read() if args.input == "-" else Path(args.input).read_text(encoding="utf-8")
    optimized, blocks = optimize_tac(source)
    if args.output:
        Path(args.output).write_text(optimized, encoding="utf-8")
    else:
        sys.stdout.write(optimized)
    if args.blocks:
        print("\n# Basic blocks and successors", file=sys.stderr)
        for block in blocks:
            print(f"{block.name}: {', '.join(block.successors) or '(exit)'}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
