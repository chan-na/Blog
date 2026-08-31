#!/usr/bin/env python3
"""Pull the translatable strings out of masked blocks, and splice them back.

    block_labels.py extract <blocks.json> <labels.json>
    block_labels.py apply   <blocks.json> <labels.json> <blocks_out.json>
    block_labels.py verify  <blocks_ko.json> <blocks_en.json> <labels_en.json>

A diagram block is 90% hand-placed coordinates and 10% words. Retyping the
markup to translate the words is how coordinates drift, so only the strings
move: extract writes every Korean-bearing text node (and code-block line) with
its exact span, apply splices translations back at those spans, and verify
proves the skeleton around them is byte-identical.
"""
import json
import re
import sys
import unicodedata

KOR = re.compile(r"[가-힣]")
NODE = re.compile(r">([^<>]+)<")          # text node between two tags
ATTR = re.compile(r'\b(?:aria-label|alt|title|placeholder)="([^"]*)"')
FENCE_LINE = re.compile(r"^.*$", re.M)    # code blocks: line by line


def spans(block):
    """(start, end) of every translatable string in one block, in order.

    Text nodes AND the human-readable attributes — aria-label carries the
    whole description of a diagram for a screen reader, so leaving it out
    ships an English page whose alt text is still Korean.
    """
    out = []
    if block.lstrip().startswith(("```", "~~~")):
        for m in FENCE_LINE.finditer(block):
            if KOR.search(m.group(0)):
                out.append((m.start(), m.end()))
    else:
        for pat in (NODE, ATTR):
            for m in pat.finditer(block):
                if KOR.search(m.group(1)):
                    out.append((m.start(1), m.end(1)))
        out.sort()
    return out


def extract(blocks):
    labels = []
    for bi, block in enumerate(blocks):
        for si, (a, b) in enumerate(spans(block)):
            labels.append({"block": bi, "span": si, "ko": block[a:b], "en": None})
    return labels


MARKER = re.compile(r"\s+([#←])")


def width(s):
    """Display columns, counting a Hangul or CJK glyph as two."""
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in s)


def realign(ko, en):
    """Keep a trailing #/← comment in the same column it sat in.

    Code blocks line their comments up by eye. Korean glyphs are two columns
    wide and English letters are one, so a translation that keeps the same
    number of spaces loses the column. Pad to the source's display column.
    """
    mk, me = MARKER.search(ko), MARKER.search(en)
    if not (mk and me):
        return en
    head, tail = en[:me.start()].rstrip(), en[me.start(1):]
    return head + " " * max(1, width(ko[:mk.start(1)]) - width(head)) + tail


def apply_(blocks, labels):
    by_block = {}
    for lab in labels:
        by_block.setdefault(lab["block"], []).append(lab)
    out = []
    for bi, block in enumerate(blocks):
        sp = spans(block)
        labs = by_block.get(bi, [])
        if len(labs) != len(sp):
            sys.exit(f"block {bi}: {len(sp)} spans but {len(labs)} labels")
        for lab in sorted(labs, key=lambda x: -x["span"]):
            a, b = sp[lab["span"]]
            if block[a:b] != lab["ko"]:
                sys.exit(f"block {bi} span {lab['span']}: source drifted")
            if lab.get("en") is None:
                sys.exit(f"block {bi} span {lab['span']}: no translation")
            block = block[:a] + realign(lab["ko"], lab["en"]) + block[b:]
        out.append(block)
    return out


def skeleton(block, strings):
    """The block with its translatable strings cut out — the markup skeleton.

    Recomputed from the label list, not from the Korean regex: the translated
    side has no Korean left in it, so it has to be told where its strings are.
    """
    parts, pos = [], 0
    for s in strings:
        i = block.find(s, pos)
        if i < 0:
            sys.exit(f"string not found in translated block: {s!r}")
        parts.append(block[pos:i])
        pos = i + len(s)
    parts.append(block[pos:])
    return "\x00".join(parts)


def main():
    mode = sys.argv[1]
    if mode == "extract":
        blocks = json.load(open(sys.argv[2], encoding="utf-8"))
        labels = extract(blocks)
        json.dump(labels, open(sys.argv[3], "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        print(f"{len(labels)} string(s) from {len(blocks)} block(s)"
              f" — {sum(len(l['ko']) for l in labels)} chars to translate")
    elif mode == "apply":
        blocks = json.load(open(sys.argv[2], encoding="utf-8"))
        labels = json.load(open(sys.argv[3], encoding="utf-8"))
        out = apply_(blocks, labels)
        json.dump(out, open(sys.argv[4], "w", encoding="utf-8"), ensure_ascii=False)
        print(f"spliced {len(labels)} string(s) into {len(out)} block(s)")
    elif mode == "verify":
        a = json.load(open(sys.argv[2], encoding="utf-8"))
        b = json.load(open(sys.argv[3], encoding="utf-8"))
        labels = json.load(open(sys.argv[4], encoding="utf-8"))
        if len(a) != len(b):
            sys.exit(f"block count differs: {len(a)} vs {len(b)}")
        per_block = {}
        for lab in labels:
            per_block.setdefault(lab["block"], []).append(lab)
        bad = []
        for i in range(len(a)):
            labs = sorted(per_block.get(i, []), key=lambda x: x["span"])
            if skeleton(a[i], [l["ko"] for l in labs]) != skeleton(b[i], [l["en"] for l in labs]):
                bad.append(i)
        if bad:
            sys.exit(f"markup differs in block(s) {bad}")
        n = sum(len(v) for v in per_block.values())
        print(f"markup identical in all {len(a)} block(s) — only the {n} strings changed")
    else:
        sys.exit(f"unknown mode: {mode}")


if __name__ == "__main__":
    main()
