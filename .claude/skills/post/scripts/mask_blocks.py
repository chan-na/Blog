#!/usr/bin/env python3
"""Hide non-prose blocks behind placeholders so a humanize pass only sees prose.

    mask_blocks.py mask   <body.md>   <masked.md> <blocks.json>
    mask_blocks.py unmask <masked.md> <blocks.json> <body.md>

Masked: fenced code blocks, and top-level raw HTML blocks (a line starting at
column 0 with <style>, <figure>, <div>, <svg>, <table>, <script>, <details>,
<pre> through the matching closing tag at column 0).

Each block becomes a line of its own: KEEP-00, KEEP-01, ... in source order.
unmask fails loudly (exit 3) if a placeholder was dropped, duplicated or
reordered, so a mangled humanize pass can never silently eat a diagram.
"""
import json
import re
import sys

HTML_TAGS = "style|figure|div|svg|table|script|details|pre"
OPEN_RE = re.compile(rf"^<({HTML_TAGS})\b", re.I)
FENCE_RE = re.compile(r"^(```|~~~)")
MARK = "⟦KEEP-{:02d}⟧"
MARK_RE = re.compile(r"⟦KEEP-(\d+)⟧")


def mask(text):
    lines = text.split("\n")
    out, blocks = [], []
    i = 0
    while i < len(lines):
        line = lines[i]
        fence = FENCE_RE.match(line)
        html = OPEN_RE.match(line)
        if not (fence or html):
            out.append(line)
            i += 1
            continue
        start = i
        i += 1
        if fence:
            marker = fence.group(1)
            while i < len(lines) and not lines[i].startswith(marker):
                i += 1
            i = min(i + 1, len(lines))  # consume the closing fence
        else:
            close = re.compile(rf"^</{html.group(1)}>", re.I)
            while i < len(lines) and not close.match(lines[i]):
                i += 1
            i = min(i + 1, len(lines))
        blocks.append("\n".join(lines[start:i]))
        out.append(MARK.format(len(blocks) - 1))
    return "\n".join(out), blocks


def unmask(text, blocks):
    seen = []

    def sub(m):
        n = int(m.group(1))
        seen.append(n)
        return blocks[n]

    restored = MARK_RE.sub(sub, text)
    if seen != list(range(len(blocks))):
        missing = sorted(set(range(len(blocks))) - set(seen))
        print(
            f"placeholder mismatch: expected {list(range(len(blocks)))}, got {seen}"
            + (f" (missing {missing})" if missing else ""),
            file=sys.stderr,
        )
        sys.exit(3)
    return restored


def main():
    mode, src, a, b = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    text = open(src, encoding="utf-8").read()
    if mode == "mask":
        masked, blocks = mask(text)
        open(a, "w", encoding="utf-8").write(masked)
        json.dump(blocks, open(b, "w", encoding="utf-8"), ensure_ascii=False)
        print(f"masked {len(blocks)} block(s) -> {a}")
    elif mode == "unmask":
        blocks = json.load(open(a, encoding="utf-8"))
        open(b, "w", encoding="utf-8").write(unmask(text, blocks))
        print(f"restored {len(blocks)} block(s) -> {b}")
    else:
        sys.exit(f"unknown mode: {mode}")


if __name__ == "__main__":
    main()
