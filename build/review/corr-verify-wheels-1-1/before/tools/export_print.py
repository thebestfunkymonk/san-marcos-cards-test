"""Print export for HEADWATERS (brief §B.1 bleed, §K layers).

    .venv/bin/python tools/export_print.py            # all cards in cards/
    .venv/bin/python tools/export_print.py KS BACK    # just these stems

For every card SVG in cards/ it writes, under print/:

    bleed/<STEM>.svg      825 × 1125 (0.125 in bleed each side). The rounded
                          card clip becomes the bleed rectangle; only the stock
                          extends — no art crosses trim, so nothing else needs bleed.
    plates/<STEM>-<ink>.svg   one black separation per printing ink
                          (jade, red, gold, ink), with the other plates removed.
                          Knockouts are geometric, so each plate is exact.
    png/<STEM>.png        825 px preview of the bleed file.

plus print/HEADWATERS-bleed.pdf (every card, one page each, 2.75 × 3.75 in)
and print/HEADWATERS-trim.pdf (trim size, rounded corners, for proofing).

The stock (paper layer) is Limestone #F4EFE3 for design; print on ivory stock
with no tint plate, or on white — see brief §0.3.
"""
from __future__ import annotations

import copy
import os
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from deck import tokens as T  # noqa: E402

SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)
Q = lambda tag: f"{{{SVG_NS}}}{tag}"  # noqa: E731

B = T.BLEED
BW, BH = T.W + 2 * B, T.H + 2 * B
PLATES = ("jade", "red", "gold", "ink")
# Deck order: A 2..10 J Q K per suit, then jokers and back (same as the contact sheet).
ORDER = ([f"{r}{s}" for s in T.SUITS for r in ("A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K")]
         + ["JOKER-RED", "JOKER-BLACK", "BACK"])


def _bleed_tree(tree: ET.ElementTree) -> ET.ElementTree:
    t = copy.deepcopy(tree)
    root = t.getroot()
    root.set("viewBox", f"{-B:g} {-B:g} {BW:g} {BH:g}")
    root.set("width", f"{BW:g}")
    root.set("height", f"{BH:g}")
    rect_d = f"M{-B:g} {-B:g}H{T.W + B:g}V{T.H + B:g}H{-B:g}Z"
    for cp in root.iter(Q("clipPath")):
        if cp.get("id") == "card":
            for p in cp.findall(Q("path")):
                p.set("d", rect_d)
    for g in root.findall(Q("g")):
        if g.get("id") == "paper":
            for p in g.iter(Q("path")):
                if p.get("class") == "stock":
                    p.set("d", rect_d)
    return t


def _plate_tree(tree: ET.ElementTree, keep: str) -> ET.ElementTree | None:
    t = copy.deepcopy(tree)
    root = t.getroot()
    found = False
    for g in list(root.findall(Q("g"))):
        gid = g.get("id")
        if gid in T.LAYERS:
            if gid != keep:
                root.remove(g)
            else:
                found = len(list(g.iter())) > 1
                for el in g.iter():
                    for attr in ("fill", "stroke"):
                        v = el.get(attr)
                        if v and v.lower() not in ("none", "transparent"):
                            el.set(attr, "#000000")
    return t if found else None


def export(stems: list[str]) -> None:
    out = os.path.join(ROOT, "print")
    for sub in ("bleed", "plates", "png"):
        os.makedirs(os.path.join(out, sub), exist_ok=True)
    bleed_paths, trim_paths = [], []
    for stem in stems:
        src = os.path.join(ROOT, "cards", f"{stem}.svg")
        if not os.path.isfile(src):
            print(f"skip {stem}: {src} missing")
            continue
        tree = ET.parse(src)
        bleed = os.path.join(out, "bleed", f"{stem}.svg")
        _bleed_tree(tree).write(bleed, encoding="unicode", xml_declaration=False)
        bleed_paths.append(bleed)
        trim_paths.append(src)
        for ink in PLATES:
            pt = _plate_tree(_bleed_tree(tree), ink)
            path = os.path.join(out, "plates", f"{stem}-{ink}.svg")
            if pt is not None:
                pt.write(path, encoding="unicode", xml_declaration=False)
            elif os.path.exists(path):
                os.remove(path)
        subprocess.run(["rsvg-convert", "-w", f"{BW:g}", bleed, "-o", os.path.join(out, "png", f"{stem}.png")],
                       check=True)
    if bleed_paths:
        subprocess.run(["rsvg-convert", "-f", "pdf", "-o", os.path.join(out, "HEADWATERS-bleed.pdf"), *bleed_paths],
                       check=True)
        subprocess.run(["rsvg-convert", "-f", "pdf", "-o", os.path.join(out, "HEADWATERS-trim.pdf"), *trim_paths],
                       check=True)
    print(f"exported {len(bleed_paths)} card(s) -> {out}/ (bleed/, plates/, png/, HEADWATERS-bleed.pdf, "
          f"HEADWATERS-trim.pdf)")


if __name__ == "__main__":
    args = sys.argv[1:]
    export([a.replace("_", "-").upper() for a in args] if args else ORDER)
