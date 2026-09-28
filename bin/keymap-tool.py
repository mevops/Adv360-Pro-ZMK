#!/usr/bin/env python3
"""Inspect, verify and re-align the Advantage 360 keymap.

The keymap's bindings are laid out as a column grid matching the physical
keyboard. Any edit that changes a binding's width breaks that grid, so this
re-flows it from the key positions in assets/key-positions.md.

  keymap-tool.py check           verify every layer: 76 bindings, columns aligned
  keymap-tool.py show <layer>    print each slot number with its binding
  keymap-tool.py find <regex>    locate a binding across all layers
  keymap-tool.py fix             re-align every layer in place (whitespace only)

check exits non-zero on failure, so it works as a pre-commit gate.
"""
import argparse, re, sys
from pathlib import Path

KEYMAP = Path(__file__).resolve().parent.parent / "config" / "adv360.keymap"

# Physical grid: 7 left columns | 3 left-thumb | 3 right-thumb | 7 right columns.
# Row membership is the key layout from assets/key-positions.md — rows 3 and 4
# are short, and the right hand shifts inward on each.
LEFT, LT, RT, RIGHT = range(4)
ROWS = [
    [(LEFT, c) for c in range(7)] + [(RIGHT, c) for c in range(7)],
    [(LEFT, c) for c in range(7)] + [(RIGHT, c) for c in range(7)],
    [(LEFT, c) for c in range(7)] + [(LT, 1), (LT, 2)] + [(RT, 0), (RT, 1)]
        + [(RIGHT, c) for c in range(7)],
    [(LEFT, c) for c in range(6)] + [(LT, 2)] + [(RT, 0)]
        + [(RIGHT, c) for c in range(1, 7)],
    [(LEFT, c) for c in range(5)] + [(LT, c) for c in range(3)]
        + [(RT, c) for c in range(3)] + [(RIGHT, c) for c in range(2, 7)],
]
NSLOTS = sum(len(r) for r in ROWS)
assert NSLOTS == 76

ORDER = ([(LEFT, c) for c in range(7)] + [(LT, c) for c in range(3)]
         + [(RT, c) for c in range(3)] + [(RIGHT, c) for c in range(7)])
BINDING = re.compile(r'&[A-Za-z_]+(?:\s+[A-Za-z0-9_()]+)*')
INDENT = " " * 8


def layer_blocks(src):
    """Yield (name, start, end) for each layer's bindings body."""
    for m in re.finditer(r'(\n\s*(\w+)\s*\{[^{}]*?bindings\s*=\s*<\n)(.*?)(\n\s*>;)',
                         src, re.S):
        yield m.group(2), m.start(3), m.end(3)


def tokens(text):
    return BINDING.findall(text)


def render(toks):
    rows, i = [], 0
    for spec in ROWS:
        rows.append(list(zip(spec, toks[i:i + len(spec)])))
        i += len(spec)
    width = {}
    for row in rows:
        for key, tok in row:
            width[key] = max(width.get(key, 0), len(tok))
    out = []
    for row in rows:
        cells, parts, prev = dict(row), [], None
        for key in ORDER:
            if prev is not None and key[0] != prev:
                parts.append("  ")           # gutter between hand/thumb blocks
            parts.append(cells.get(key, "").ljust(width.get(key, 0)))
            prev = key[0]
        out.append((INDENT + " ".join(parts)).rstrip())
    return "\n".join(out)


BLOCK = {LEFT: "L", LT: "LT", RT: "RT", RIGHT: "R"}


def colname(key):
    return f"{BLOCK[key[0]]}{key[1]}"


def slot_names():
    names, counts = [], BLOCK
    for spec in ROWS:
        for blk, col in spec:
            names.append(f"{counts[blk]}{col}")
    return names


def problems(body):
    """Return a list of layout faults in one layer's bindings body, [] if sound.

    Alignment is judged only on whether each grid column starts at a consistent
    offset across rows. Upstream pads some layers differently to this tool's
    renderer; that is not a fault and must not be "corrected", or every edit
    drags unrelated layers into the diff.
    """
    faults, toks = [], tokens(body)
    if len(toks) != NSLOTS:
        return [f"{len(toks)} bindings, expected {NSLOTS}"]
    offsets = {}
    for n, (line, spec) in enumerate(zip(body.split("\n"), ROWS)):
        found = [(m.start(), m.group(0)) for m in BINDING.finditer(line)]
        if len(found) != len(spec):
            faults.append(f"row {n} has {len(found)} bindings, expected {len(spec)}")
            continue
        for (off, _), key in zip(found, spec):
            if key in offsets and offsets[key] != off:
                faults.append(f"row {n} column {colname(key)} starts at col {off}, "
                              f"elsewhere at {offsets[key]}")
            offsets.setdefault(key, off)
    return faults


def cmd_check(src):
    bad = False
    for name, s, e in layer_blocks(src):
        faults = problems(src[s:e])
        if faults:
            bad = True
            print(f"  BAD {name}")
            for f in faults:
                print(f"        {f}")
        else:
            print(f"  OK  {name:15} {len(tokens(src[s:e]))} bindings, columns aligned")
    return 1 if bad else 0


def cmd_show(src, layer):
    names = slot_names()
    for name, s, e in layer_blocks(src):
        if name != layer:
            continue
        for i, tok in enumerate(tokens(src[s:e])):
            print(f"  {i:3}  {names[i]:5}  {tok}")
        return 0
    print(f"no layer named {layer!r}", file=sys.stderr)
    return 1


def cmd_find(src, pattern):
    rx, names, hits = re.compile(pattern), slot_names(), 0
    for name, s, e in layer_blocks(src):
        for i, tok in enumerate(tokens(src[s:e])):
            if rx.search(tok):
                print(f"  {name:15} slot {i:3}  {names[i]:5}  {tok}")
                hits += 1
    return 0 if hits else 1


def cmd_fix(src, path):
    out, changed = src, []
    for name, s, e in reversed(list(layer_blocks(src))):
        faults = problems(out[s:e])
        if not faults:
            continue                     # already sound - leave it exactly as it is
        toks = tokens(out[s:e])
        if len(toks) != NSLOTS:
            print(f"  refusing to fix {name}: {len(toks)} bindings, expected "
                  f"{NSLOTS} - add or remove bindings first", file=sys.stderr)
            return 1
        out = out[:s] + render(toks) + out[e:]
        changed.append(name)
    # bindings must survive a re-flow untouched
    assert tokens(out) == tokens(src), "re-align altered a binding; aborted"
    path.write_text(out)
    print("  re-aligned:", ", ".join(reversed(changed)) if changed else "nothing to do")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["check", "show", "find", "fix"])
    ap.add_argument("arg", nargs="?")
    a = ap.parse_args()
    src = KEYMAP.read_text()
    if a.command == "check":
        return cmd_check(src)
    if a.command == "show":
        return cmd_show(src, a.arg or "default_layer")
    if a.command == "find":
        if not a.arg:
            ap.error("find needs a pattern")
        return cmd_find(src, a.arg)
    return cmd_fix(src, KEYMAP)


if __name__ == "__main__":
    sys.exit(main())
