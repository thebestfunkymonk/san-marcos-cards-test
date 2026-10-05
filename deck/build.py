"""Build the deck: cards/*.svg, build/png/*.png (750 w), build/png/small/*.png
(188 w) and build/contact.png.

    .venv/bin/python -m deck.build                 # all 55 pieces
    .venv/bin/python -m deck.build KS 10H AS       # just these (IDs or file stems)
    .venv/bin/python -m deck.build numbers courts  # groups: numbers courts aces jokers back all
    .venv/bin/python -m deck.build all --stock white   # QA variant -> build/white/...
    .venv/bin/python -m deck.build all --print         # + §B.1 825 x 1125 bleed files -> build/print/

Piece IDs (art-module names): 2S…10D, KS QS JS … JD, AS AH AC AD,
JOKER_RED, JOKER_BLACK, BACK. File stems follow brief §K: KS, 10H,
JOKER-RED, JOKER-BLACK, BACK.

Courts are two-headed in one of two modes (deck/ART_CONTRACT.md §3.1): the
legacy BAND mode (art clipped at y 511, divider band + partition line + rank
medallion) or, when the module sets ``DOUBLE_HEAD = "continuous"``, the
CONTINUOUS mode (art clipped along the module's C2 ``SEAM``; no band,
partition or medallion; the halves meet invisibly). The manifest records
``double_head`` and, for continuous courts, the ``seam`` polyline.

Pieces whose art module (``art/<ID>.py``) is missing, or fails, build as a
tasteful placeholder (frame / pip only), so the full deck always builds. The
build writes ``build/manifest.json`` (one record per piece) for ``deck.qa``.
"""
from __future__ import annotations

import argparse
import importlib
import importlib.util
import json
import os
import subprocess
import sys
import time
import traceback
from concurrent.futures import ProcessPoolExecutor

from inkkit import geom as G
from inkkit import svg as S
from deck import tokens as T
from deck import cardsvg as C
from deck import frames as F
from deck import index as IX
from deck import layout as LY

ROOT = str(T.ROOT)
NUM_RANKS = ("2", "3", "4", "5", "6", "7", "8", "9", "10")
COURT_RANKS = ("K", "Q", "J")
SMALL_W = 188
FULL_W = 750

# -----------------------------------------------------------------------------
# piece catalogue
# -----------------------------------------------------------------------------
ALL_IDS = ([f"A{s}" for s in T.SUITS] +
           [f"{r}{s}" for s in T.SUITS for r in NUM_RANKS] +
           [f"{r}{s}" for s in T.SUITS for r in COURT_RANKS] +
           ["JOKER_RED", "JOKER_BLACK", "BACK"])
GROUPS = {
    "all": ALL_IDS,
    "numbers": [f"{r}{s}" for s in T.SUITS for r in NUM_RANKS],
    "courts": [f"{r}{s}" for s in T.SUITS for r in COURT_RANKS],
    "aces": [f"A{s}" for s in T.SUITS],
    "jokers": ["JOKER_RED", "JOKER_BLACK"],
    "back": ["BACK"],
}
# contact-sheet order: A 2..10 J Q K per suit row, then jokers + back
SHEET_ORDER = ([f"{r}{s}" for s in T.SUITS for r in ("A",) + NUM_RANKS + ("J", "Q", "K")] +
               ["JOKER_RED", "JOKER_BLACK", "BACK"])


def stem(pid: str) -> str:
    """File stem for a piece ID (§K): JOKER_RED -> JOKER-RED."""
    return pid.replace("_", "-")


def normalize(token: str) -> list[str]:
    t = token.strip().upper().replace("-", "_")
    if t.lower() in GROUPS:
        return list(GROUPS[t.lower()])
    t = {"JOKER_BIG": "JOKER_RED", "JOKER_LITTLE": "JOKER_BLACK"}.get(t, t)
    if t not in ALL_IDS:
        raise SystemExit(f"unknown piece {token!r}; e.g. KS 10H AS JOKER_RED BACK or a group "
                         f"({', '.join(GROUPS)})")
    return [t]


def parse(pid: str) -> dict:
    """{'id', 'stem', 'kind', 'rank', 'suit'}; kind in number|court|ace|joker|back."""
    if pid == "BACK":
        return {"id": pid, "stem": stem(pid), "kind": "back", "rank": None, "suit": None}
    if pid.startswith("JOKER"):
        return {"id": pid, "stem": stem(pid), "kind": "joker", "rank": "JOKER", "suit": None,
                "color": "red" if pid == "JOKER_RED" else "ink"}
    rank, suit = pid[:-1], pid[-1]
    kind = "ace" if rank == "A" else "court" if rank in COURT_RANKS else "number"
    return {"id": pid, "stem": stem(pid), "kind": kind, "rank": rank, "suit": suit}


# -----------------------------------------------------------------------------
# art modules
# -----------------------------------------------------------------------------
def load_art(pid: str):
    """Import ``art/<ID>.py`` (fresh), or None when it does not exist."""
    path = os.path.join(ROOT, "art", f"{pid}.py")
    if not os.path.isfile(path):
        return None
    name = f"art.{pid}"
    sys.modules.pop(name, None)
    return importlib.import_module(name)


# -----------------------------------------------------------------------------
# placeholders (frame / pip only)
# -----------------------------------------------------------------------------
def placeholder_ace(suit: str) -> dict:
    col, layer = T.SUIT_COLOR[suit], T.SUIT_LAYER[suit]
    out = {layer: [S.path(F.ace_pip_d(suit), fill=col, class_="ace-pip placeholder")]}
    if suit != "S":
        out["gold"] = [S.path(F.ace_keyline_d(suit), fill="none", stroke=T.FOIL, stroke_width=T.FINE,
                              stroke_linejoin="miter", stroke_miterlimit=10, class_="ace-keyline placeholder")]
    return out


def placeholder_joker(color_layer: str) -> dict:
    return {"gold": F.joker_rule_fragments(T.FOIL)}


def placeholder_back() -> dict:
    """Jade flood with the frame rules and lens reversed out geometrically
    (flood minus stroke outlines) — the back's structure, no ornament."""
    fx0, fy0 = T.SAFE, T.SAFE
    flood = G.rect_d(fx0, fy0, T.W - 2 * fx0, T.H - 2 * fy0, 18)
    rules = []
    rules.append(G.outline(G.rect_d(49.5, 49.5, T.W - 99, T.H - 99, 0), T.RULE, cap="butt", join="miter"))
    rules.append(G.outline(G.rect_d(57.5, 57.5, T.W - 115, T.H - 115, 0), T.FINE, cap="butt", join="miter"))
    R = 463.2
    lens = G.intersection(G.circle_d(181.8, 525, R), G.circle_d(568.2, 525, R))
    rules.append(G.outline(lens, T.FINE, join="miter", miter_limit=10))
    rules.append(G.outline(G.offset(lens, -6, join="miter", miter_limit=10), T.FINE, join="miter",
                           miter_limit=10))
    ko = G.difference(flood, *rules)
    return {"jade": [S.path(ko, fill=T.JADE, fill_rule="nonzero", class_="flood placeholder")]}


# -----------------------------------------------------------------------------
# one card
# -----------------------------------------------------------------------------
def build_piece(pid: str, stock: str = "limestone", print_file: bool = False) -> dict:
    info = parse(pid)
    kind, rank, suit = info["kind"], info["rank"], info["suit"]
    order = C.ACE_ORDER if pid in ("AS", "AC") else T.LAYERS
    doc = C.CardDoc(stem(pid), stock=stock, order=order,
                    title=f"HEADWATERS {stem(pid)}")
    status, err = "system", None

    art = None
    if kind in ("court", "ace", "joker", "back"):
        try:
            mod = load_art(pid)
            if mod is not None:
                art = C.layers_merge(mod.build())
                info["cut_y"] = getattr(mod, "CUT_Y", F.BAND_Y0)
                if kind == "court":
                    info["double_head"] = F.double_head_mode(mod)
                    if info["double_head"] == "continuous":
                        info["seam"] = F.seam_spec(getattr(mod, "SEAM", None))
        except Exception:
            err = traceback.format_exc(limit=6)
            art = None
        status = "art" if art is not None else "placeholder"

    if kind == "number":
        doc.add_layers(LY.pip_card_fragments(rank, suit))
        doc.add_layers(IX.index_fragments(rank, suit))
    elif kind == "court":
        mode = info.get("double_head", "band") if art is not None else "band"
        info["double_head"] = mode
        if art is not None and mode == "continuous":
            # ART_CONTRACT §3.1b: clip to the seam's top side, add the 180° copy;
            # no band, partition, medallion or seam line
            doc.add_layers(C.continuous_two_headed(art, info["seam"]["points"]))
        elif art is not None:
            clip = F.court_clip_d(rank, info.get("cut_y", F.BAND_Y0))
            doc.add_layers(C.two_headed(art, clip))
        doc.add_layers(F.court_frame_fragments(rank, suit, double_head=mode))
        doc.add_layers(IX.index_fragments(rank, suit))
    elif kind == "ace":
        doc.add_layers(art if art is not None else placeholder_ace(suit))
        doc.add_layers(IX.index_fragments("A", suit))
    elif kind == "joker":
        doc.add_layers(art if art is not None else placeholder_joker(info["color"]))
        doc.add_layers(IX.joker_index_fragments(info["color"]))
    elif kind == "back":
        doc.add_layers(art if art is not None else placeholder_back())

    out_root = ROOT if stock == "limestone" else os.path.join(ROOT, "build", "white")
    svg_path = os.path.join(out_root, "cards", f"{stem(pid)}.svg")
    doc.save(svg_path)
    print_path = None
    if print_file:
        sub = "print" if stock == "limestone" else os.path.join("white", "print")
        print_path = doc.save(os.path.join(ROOT, "build", sub, f"{stem(pid)}.svg"), bleed=True)
    png_dir = os.path.join(ROOT, "build", "png") if stock == "limestone" else os.path.join(out_root, "png")
    png = os.path.join(png_dir, f"{stem(pid)}.png")
    small = os.path.join(png_dir, "small", f"{stem(pid)}.png")
    os.makedirs(os.path.dirname(small), exist_ok=True)
    for w, p in ((FULL_W, png), (SMALL_W, small)):
        r = subprocess.run(["rsvg-convert", "-w", str(w), svg_path, "-o", p], capture_output=True, text=True)
        if r.returncode:
            raise RuntimeError(f"rsvg-convert failed for {pid}: {r.stderr.strip()}")
    info.update({"status": status, "stock": stock, "order": list(order), "svg": svg_path, "png": png,
                 "small": small, "print": print_path, "error": err})
    return info


def _build_one(args):
    pid, stock, print_file = (args + (False,))[:3]
    t0 = time.time()
    try:
        info = build_piece(pid, stock, print_file)
    except Exception:
        info = parse(pid)
        info.update({"status": "failed", "error": traceback.format_exc(limit=8), "stock": stock})
    info["seconds"] = round(time.time() - t0, 2)
    return info


# -----------------------------------------------------------------------------
# contact sheet
# -----------------------------------------------------------------------------
def contact_sheet(records: list[dict], out_png: str, cell_w: int = SMALL_W, cols: int = 13) -> str:
    from PIL import Image, ImageDraw, ImageFont
    by = {r["id"]: r for r in records}
    ids = [i for i in SHEET_ORDER if i in by and os.path.isfile(by[i].get("small", ""))]
    if not ids:
        return ""
    cell_h = int(round(cell_w * T.H / T.W))
    gap, label_h, margin = 14, 22, 24
    rows = []
    for s in T.SUITS:
        row = [i for i in ids if i[-1] == s and not i.startswith("JOKER") and i != "BACK"]
        if row:
            rows.append(row)
    extra = [i for i in ids if i.startswith("JOKER") or i == "BACK"]
    if extra:
        rows.append(extra)
    ncols = max(len(r) for r in rows)
    W = margin * 2 + ncols * cell_w + (ncols - 1) * gap
    H = margin * 2 + len(rows) * (cell_h + label_h) + (len(rows) - 1) * gap
    sheet = Image.new("RGB", (W, H), (43, 43, 43))
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype(str(T.FONT_INDEX), 15)
    except Exception:
        font = ImageFont.load_default()
    mask = Image.new("L", (cell_w, cell_h), 0)
    rr = int(round(T.CORNER_R * cell_w / T.W))
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, cell_w - 1, cell_h - 1], rr, fill=255)
    for ri, row in enumerate(rows):
        for ci, pid in enumerate(row):
            im = Image.open(by[pid]["small"]).convert("RGBA")
            if im.size != (cell_w, cell_h):
                im = im.resize((cell_w, cell_h), Image.LANCZOS)
            x = margin + ci * (cell_w + gap)
            y = margin + ri * (cell_h + label_h + gap)
            sheet.paste(im.convert("RGB"), (x, y), mask)
            lab = stem(pid) + ("" if by[pid]["status"] in ("art", "system") else " · " + by[pid]["status"])
            tw = draw.textlength(lab, font=font)
            draw.text((x + (cell_w - tw) / 2, y + cell_h + 3), lab, fill=(200, 196, 186), font=font)
    os.makedirs(os.path.dirname(out_png), exist_ok=True)
    sheet.save(out_png)
    return out_png


# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------
def build(ids: list[str], stock: str = "limestone", jobs: int | None = None, sheet: bool = True,
          print_files: bool = False) -> list[dict]:
    jobs = jobs or min(len(ids), os.cpu_count() or 4)
    if jobs > 1 and len(ids) > 1:
        with ProcessPoolExecutor(jobs) as ex:
            recs = list(ex.map(_build_one, [(i, stock, print_files) for i in ids]))
    else:
        recs = [_build_one((i, stock, print_files)) for i in ids]
    base = os.path.join(ROOT, "build") if stock == "limestone" else os.path.join(ROOT, "build", "white")
    man_path = os.path.join(base, "manifest.json")
    manifest = {}
    if os.path.isfile(man_path):
        try:
            manifest = {r["id"]: r for r in json.load(open(man_path))}
        except Exception:
            manifest = {}
    for r in recs:
        manifest[r["id"]] = r
    os.makedirs(base, exist_ok=True)
    allrecs = [manifest[i] for i in ALL_IDS if i in manifest]
    json.dump(allrecs, open(man_path, "w"), indent=1)
    if sheet:
        contact_sheet(allrecs, os.path.join(base, "contact.png"))
    return recs


def main(argv=None):
    ap = argparse.ArgumentParser(prog="deck.build", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ids", nargs="*", default=["all"], help="piece IDs / file stems / groups")
    ap.add_argument("--stock", choices=sorted(C.STOCKS), default="limestone",
                    help="paper colour; 'white' writes a QA variant under build/white/")
    ap.add_argument("-j", "--jobs", type=int, default=None)
    ap.add_argument("--no-sheet", action="store_true", help="skip the contact sheet")
    ap.add_argument("--print", dest="print_files", action="store_true",
                    help="also write §B.1 print files (825 x 1125, paper extended 37.5 px) to build/print/")
    a = ap.parse_args(argv)
    ids = []
    for t in a.ids:
        for i in normalize(t):
            if i not in ids:
                ids.append(i)
    t0 = time.time()
    recs = build(ids, a.stock, a.jobs, sheet=not a.no_sheet, print_files=a.print_files)
    dt = time.time() - t0
    bad = [r for r in recs if r["status"] == "failed"]
    ph = [r["id"] for r in recs if r["status"] == "placeholder"]
    for r in recs:
        if r.get("error"):
            print(f"--- {r['id']} ({r['status']}):\n{r['error']}", file=sys.stderr)
    print(f"built {len(recs)} piece(s) on {a.stock} in {dt:.1f}s"
          + (f"; placeholders: {' '.join(ph)}" if ph else "")
          + (f"; FAILED: {' '.join(r['id'] for r in bad)}" if bad else ""))
    base = "build" if a.stock == "limestone" else "build/white"
    print(f"svg: {'cards' if a.stock == 'limestone' else base + '/cards'}/  png: {base}/png/  "
          f"sheet: {base}/contact.png" + (f"  print: {base}/print/" if a.print_files else ""))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
