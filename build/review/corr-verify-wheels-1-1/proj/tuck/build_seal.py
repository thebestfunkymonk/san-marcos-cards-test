"""Build and check the HEADWATERS seal — creative brief §H.20 "Seal", §B.1 (Ø330), §B.2, §C, §D, §G, §J.2.

    .venv/bin/python tuck/build_seal.py            (run from the project root)
    .venv/bin/python -m tuck.build_seal            (the same)

Writes
    tuck/SEAL.svg                 print file (300 ppi, 405 px square = Ø330 + 37.5 px bleed each side), plates
                                  in print order: <g id="board"> Gill Red paper stock, <g id="emboss"> (empty —
                                  the seal is foil only, §C), <g id="foil"> flat Lion Gold foil (every stroke a
                                  §B.2 width, type outlined), <g id="dieline"> the 24-lobe ripple die-cut
                                  (registration magenta, NON-PRINTING).
    build/tuck/SEAL.png           flat print preview, die-cut, 1:1 (330 px)
    build/tuck/SEAL@3x.png        the same at 3× (990 px) for detail review
    build/tuck/SEAL-83.png        thumbnail (25 %)
    build/tuck/SEAL-print.png     the whole print file (bleed + dieline) at 2×
    build/tuck/SEAL-mock.png      mock-up: FOIL_PREVIEW gradient foil on the die-cut red seal, on Deep Hole
                                  board (mock-ups only — never in the print file, §C)
    build/tuck/SEAL-mock-small.png  the mock-up at thumbnail size
    build/tuck/SEAL-qa/           SEAL-qa.json (the check row + details), detail crops at 5×, flag overlay

QA row (✓ pass, ✗ fail, ! look at the flag overlay):
    1  strk   every foil stroke width in {1.6, 2.1, 3.1, 4.2, 6.25}; no transform attributes
    4  pal    foil plate = flat Lion Gold only; board = Gill Red only; no board-coloured paint in the foil
    8  safe   all foil ≥ 10 px inside the die's troughs (registration), type inside the text band
    12 gaps   the foil AS STAMPED (union of every mark): separate pieces ≥ 3.0 apart and ≥ 4.2 where they
              run alongside for ≥ 12 px; enclosed board ≥ 2.5 wide; no piece thinner than HAIRLINE
              (tuck.build_tuck.foil_gaps) + raster: foil features < 1.5 px, tight board < 4.2 px (warn)
    17 svg    no <text>/<use>/filters/gradients/…; plates board, emboss, foil, dieline in order
    25 rndr   rsvg-convert vs resvg agree
    copy      NUSQUAM ALIBI / SAN MARCOS · TEXAS verbatim from §J.2
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

from deck import tokens as T  # noqa: E402
from deck.motifs.core import Frag  # noqa: E402

import _seal_ring as R  # noqa: E402
import _seal_salamander as SAL  # noqa: E402

OUT_SVG = os.path.join(HERE, "SEAL.svg")
BUILD = os.path.join(ROOT, "build", "tuck")
QA = os.path.join(BUILD, "SEAL-qa")

BLEED = T.BLEED                    # 37.5
SIZE = 2 * R.R_PEAK + 2 * BLEED    # 405
CX = CY = SIZE / 2                 # 202.5
REG = "#FF00FF"                    # dieline: registration magenta, non-printing
NS = "{http://www.w3.org/2000/svg}"

# composition
SAL_FACING = -25.0                 # the snout points up and right; the head lies across 12-1 o'clock
SAL_OFFSET = (0.0, 0.0)            # nudge from the centring (px)

J2 = {"NUSQUAM ALIBI", "SAN MARCOS · TEXAS"}          # §J.2, the seal's two lines
BANNED = {"text", "tspan", "textPath", "image", "filter", "linearGradient", "radialGradient", "pattern", "mask",
          "use", "symbol", "marker", "switch", "style", "a", "foreignObject", "script"}


def build_art():
    """Return (foil Frag, salamander Frag, info)."""
    foil = R.rings(CX, CY)
    text, tinfo = R.legend_text(CX, CY)
    foil += text
    foil += R.bubble_strings(CX, CY, tinfo["span_top"], tinfo["span_bot"])
    sal = SAL.placed(CX, CY, SAL_FACING, SAL.seal_spec(), centre="mec", offset=SAL_OFFSET)
    foil += sal
    info = dict(tinfo)
    info["sal_bbox"] = sal.bbox()
    return foil, sal, info


# -----------------------------------------------------------------------------
# SVG writers
# -----------------------------------------------------------------------------
def _num(v: float) -> str:
    s = f"{v:.3f}".rstrip("0").rstrip(".")
    return s if s != "-0" else "0"


def print_svg(foil: Frag) -> str:
    die = R.die_d(CX, CY)
    board = f'<rect x="0" y="0" width="{_num(SIZE)}" height="{_num(SIZE)}" fill="{T.RED}"/>'
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{_num(SIZE)}" height="{_num(SIZE)}" '
        f'viewBox="0 0 {_num(SIZE)} {_num(SIZE)}">',
        "<title>HEADWATERS seal — Ø330 (1.1 in) die-cut, Gill Red paper, gold foil</title>",
        "<desc>Print file at 300 ppi. board = Gill Red paper stock #AE2F2B (shown with 37.5 px bleed); "
        "emboss = none; foil = gold foil (flat preview colour #B08D57); dieline = 24-lobe ripple "
        "die-cut, registration magenta, NON-PRINTING.</desc>",
        f'<g id="board" data-stock="Gill Red paper {T.RED}">{board}</g>',
        '<g id="emboss" data-plate="blind emboss (none on the seal)"/>',
        f'<g id="foil" data-plate="gold foil">{foil.svg()}</g>',
        f'<g id="dieline" data-nonprinting="true" data-spot="CutContour">'
        f'<path d="{die}" fill="none" stroke="{REG}" stroke-width="{T.HAIRLINE}"/></g>',
        "</svg>",
    ]
    return "\n".join(parts)


def _gradient_defs(gid: str, x0, y0, x1, y1) -> str:
    a, b, c = T.FOIL_PREVIEW
    stops = [(0.0, a), (0.30, b), (0.48, c), (0.62, b), (1.0, a)]
    st = "".join(f'<stop offset="{o}" stop-color="{col}"/>' for o, col in stops)
    return (f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="{_num(x0)}" y1="{_num(y0)}" '
            f'x2="{_num(x1)}" y2="{_num(y1)}">{st}</linearGradient>')


def preview_svg(foil: Frag, *, mock: bool = False, ground: str | None = None, pad: float = 0.0,
                shadow: bool = False) -> str:
    """Die-cut preview (clipped to the die line). ``mock`` paints the foil with
    the FOIL_PREVIEW gradient (mock-ups only)."""
    die = R.die_d(CX, CY)
    x0 = CX - R.R_PEAK - pad
    w = 2 * (R.R_PEAK + pad)
    foil_svg = foil.svg()
    defs = ""
    if mock:
        defs += _gradient_defs("foilgrad", CX - 150, CY - 170, CX + 150, CY + 170)
        foil_svg = re.sub(r'(stroke|fill)="' + re.escape(T.FOIL) + '"', r'\1="url(#foilgrad)"', foil_svg)
    if shadow:
        defs += ('<filter id="sh" x="-20%" y="-20%" width="140%" height="140%">'
                 '<feGaussianBlur stdDeviation="3.2"/></filter>')
    bg = f'<rect x="{_num(x0)}" y="{_num(x0)}" width="{_num(w)}" height="{_num(w)}" fill="{ground}"/>' if ground else ""
    sh = (f'<path d="{die}" fill="#000" fill-opacity="0.45" transform="translate(1.5 3)" filter="url(#sh)"/>'
          if shadow else "")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{_num(x0)} {_num(x0)} {_num(w)} {_num(w)}" '
            f'width="{_num(w)}" height="{_num(w)}"><defs>{defs}<clipPath id="die"><path d="{die}"/></clipPath></defs>'
            f'{bg}{sh}<path d="{die}" fill="{T.RED}"/><g clip-path="url(#die)">{foil_svg}</g></svg>')


def render(svg_path: str, png_path: str, width: int) -> None:
    subprocess.run(["rsvg-convert", "-w", str(width), svg_path, "-o", png_path], check=True)


# -----------------------------------------------------------------------------
# QA
# -----------------------------------------------------------------------------
def _foil_mask(foil: Frag, scale: float) -> np.ndarray:
    """The foil plate alone rasterised at ``scale`` (bool mask, seal coordinates)."""
    from io import BytesIO
    from PIL import Image
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {_num(SIZE)} {_num(SIZE)}" '
           f'width="{int(SIZE * scale)}" height="{int(SIZE * scale)}">{foil.svg()}</svg>')
    r = subprocess.run(["rsvg-convert"], input=svg.encode(), capture_output=True, check=True)
    a = np.asarray(Image.open(BytesIO(r.stdout)).convert("RGBA"))
    return a[:, :, 3] > 127


def qa(foil: Frag, sal: Frag, info: dict, svg_text: str) -> dict:
    from deck import qa as DQ
    from deck.motifs.core import check
    from tuck.build_tuck import foil_gaps, tight_board
    from tuck import _tuck_common as K
    rep: dict = {"piece": "SEAL"}
    root = ET.fromstring(svg_text)
    plates = {g.get("id"): g for g in root if g.tag == NS + "g"}
    # 17 structure
    tags = {el.tag.replace(NS, "") for el in root.iter()}
    bad = sorted(tags & BANNED)
    order = [g.get("id") for g in root if g.tag == NS + "g"]
    rep["17_svg"] = {"ok": not bad and order == ["board", "emboss", "foil", "dieline"], "banned": bad,
                     "plates": order}
    # 1 strokes
    widths = set()
    for el in plates["foil"].iter():
        w = el.get("stroke-width")
        if w is not None and el.get("stroke") not in (None, "none"):
            widths.add(round(float(w), 3))
    illegal = sorted(w for w in widths if w not in T.LEGAL_STROKES)
    tf = [el.get("transform") for el in root.iter() if el.get("transform")]
    rep["1_strk"] = {"ok": not illegal and not tf and not check(foil), "widths": sorted(widths),
                     "illegal": illegal, "transforms": len(tf), "motif_check": check(foil)[:5]}
    # 4 palette
    cols = set()
    for el in plates["foil"].iter():
        for k in ("fill", "stroke"):
            v = el.get(k)
            if v and v != "none":
                cols.add(v.lower())
    bcols = {el.get("fill", "").lower() for el in plates["board"].iter() if el.get("fill")}
    rep["4_pal"] = {"ok": cols == {T.FOIL.lower()} and bcols == {T.RED.lower()} and not len(plates["emboss"]),
                    "foil_colours": sorted(cols), "board": sorted(bcols)}
    # 8 safe: every mark ≥ 10 px inside the die troughs; type within its band
    allg = foil.shape()
    trough = R.R_PEAK - R.RIPPLE
    pts = np.vstack([np.asarray(g.exterior.coords) for g in getattr(allg, "geoms", [allg])])
    r_out = float(np.max(np.hypot(pts[:, 0] - CX, pts[:, 1] - CY)))
    typ = Frag([m for m in foil.marks if m.role == "type"]).shape()
    tp = np.vstack([np.asarray(g.exterior.coords) for g in getattr(typ, "geoms", [typ])])
    tr = np.hypot(tp[:, 0] - CX, tp[:, 1] - CY)
    sh = sal.shape()
    sp = np.vstack([np.asarray(g.exterior.coords) for g in getattr(sh, "geoms", [sh])])
    s_r = float(np.max(np.hypot(sp[:, 0] - CX, sp[:, 1] - CY)))
    inner_edge = R.R_INNER_RULE - T.FINE / 2
    rep["8_safe"] = {"ok": trough - r_out >= 10.0 - 1e-6 and inner_edge + 4.2 <= float(tr.min())
                     and float(tr.max()) <= R.R_OUTER_RULE - T.RULE / 2 - 4.2 and inner_edge - s_r >= 4.2,
                     "foil_to_die_trough": round(trough - r_out, 2),
                     "type_band": [round(float(tr.min()), 2), round(float(tr.max()), 2)],
                     "type_clear_in": round(float(tr.min()) - inner_edge, 2),
                     "type_clear_out": round(R.R_OUTER_RULE - T.RULE / 2 - float(tr.max()), 2),
                     "salamander_clear_to_ring": round(inner_edge - s_r, 2)}
    # 12 gaps: the foil as stamped
    t0 = time.time()
    gaps = foil_gaps(allg, type_shape=K.type_hull(foil))
    warn_counters = [g for g in gaps if "warn" in g["rule"]]
    gaps = [g for g in gaps if "warn" not in g["rule"]]
    tb = tight_board(foil)
    scale = 4.0
    m = _foil_mask(foil, scale)
    thin = m & ~DQ._open(m, DQ.RASTER_LINE_MIN * scale / 2)
    thin_cl = DQ._clusters(thin, DQ.LINE_CLUSTER * scale * scale, scale)
    rep["12_gaps"] = {"ok": not gaps, "n": len(gaps), "worst": gaps[:12], "s": round(time.time() - t0, 1),
                      "raster_tight_board_warn": len(tb), "raster_tight_board": tb[:12],
                      "raster_thin_foil_warn": len(thin_cl), "raster_thin_foil": thin_cl[:12],
                      "type_counters_warn": [(g["gap"], g["at"]) for g in warn_counters]}
    # 25 rsvg vs resvg on the print file
    try:
        p = os.path.join(QA, "_print.svg")
        with open(p, "w") as fh:
            fh.write(svg_text)
        a = DQ._rsvg(svg_text, 810).astype(int)
        b = DQ._resvg(p, 810).astype(int)
        hh = min(a.shape[0], b.shape[0])
        frac = float((np.abs(a[:hh] - b[:hh]).max(axis=2) > 40).mean())
        rep["25_rndr"] = {"ok": frac < DQ.RENDER_DIFF_MAX, "diff_frac": round(frac, 5)}
        os.remove(p)
    except Exception as e:  # noqa: BLE001
        rep["25_rndr"] = {"ok": False, "error": str(e)[:200]}
    # copy
    used = {R.TOP_TEXT, R.BOTTOM_TEXT}
    rep["copy_J2"] = {"ok": used <= J2, "used": sorted(used)}
    # facts for the reviewer
    body = sal.meta["body"]
    rep["facts"] = {
        "hatch_lines": sal.meta.get("hatch_n"), "split_end_s": round(sal.meta.get("split_end", 0), 1),
        "spine_turn_deg": round(float(body.head[-1] - body.head[0]), 1),
        "salamander_r_max": round(s_r, 2), "font_size": round(info["size"], 3),
        "span_top_deg": round(info["span_top"], 1), "span_bot_deg": round(info["span_bot"], 1),
        "outer_rule_to_die_trough": round(trough - (R.R_OUTER_RULE + T.RULE / 2), 2),
    }
    rep["_flags"] = [g["at"] for g in gaps] + [t["at"] for t in tb[:12]] + [
        [(c["bbox"][0] + c["bbox"][2]) / 2, (c["bbox"][1] + c["bbox"][3]) / 2] for c in thin_cl[:12]]
    return rep


def flags_png(foil: Frag, rep: dict) -> None:
    marks = "".join(f'<circle cx="{_num(x)}" cy="{_num(y)}" r="6" fill="none" stroke="#00E0FF" stroke-width="1"/>'
                    for x, y in rep["_flags"])
    s = preview_svg(foil).replace("</svg>", f"<g>{marks}</g></svg>")
    p = os.path.join(QA, "SEAL-flags.svg")
    with open(p, "w") as fh:
        fh.write(s)
    render(p, os.path.join(QA, "SEAL-flags.png"), 1320)


def row(rep: dict) -> str:
    sym = lambda v: "✓" if v is True else ("✗" if v is False else "·")  # noqa: E731
    cols = ["1_strk", "4_pal", "8_safe", "12_gaps", "17_svg", "25_rndr", "copy_J2"]
    g = rep["12_gaps"]
    det = []
    if g["n"]:
        det.append(f"{g['n']} gaps, worst {g['worst'][0]['gap']} ({g['worst'][0]['rule']}) at {g['worst'][0]['at']}")
    if g["raster_tight_board_warn"]:
        det.append(f"! {g['raster_tight_board_warn']} tight-board clusters")
    if g["raster_thin_foil_warn"]:
        det.append(f"! {g['raster_thin_foil_warn']} thin-foil clusters")
    det.append(f"foil->die {rep['8_safe']['foil_to_die_trough']}")
    det.append(f"rsvg/resvg {rep['25_rndr'].get('diff_frac')}")
    head = f"{'piece':6} " + " ".join(f"{c.split('_')[0]:>5}" for c in cols)
    body = f"{'SEAL':6} " + " ".join(f"{sym(rep[c]['ok']):>5}" for c in cols) + "   " + "; ".join(det)
    return head + "\n" + body


def crops(foil: Frag, sal: Frag) -> None:
    """5× detail crops (top / bottom / left / right of the field) for review."""
    p = os.path.join(QA, "_prev.svg")
    with open(p, "w") as fh:
        fh.write(preview_svg(foil))
    big = os.path.join(QA, "_5x.png")
    render(p, big, 1650)
    x0 = CX - R.R_PEAK
    for name, (cx, cy) in (("top", (CX, CY - 55)), ("bottom", (CX, CY + 55)), ("left", (CX - 55, CY)),
                           ("right", (CX + 55, CY))):
        X = int((cx - x0 - 60) * 5)
        Y = int((cy - x0 - 60) * 5)
        subprocess.run(["magick", big, "-crop", f"600x600+{X}+{Y}", "+repage",
                        os.path.join(QA, f"SEAL-{name}-5x.png")], check=True)
    os.remove(p)
    os.remove(big)


def main():
    os.makedirs(BUILD, exist_ok=True)
    os.makedirs(QA, exist_ok=True)
    t0 = time.time()
    foil, sal, info = build_art()
    svg = print_svg(foil)
    with open(OUT_SVG, "w") as fh:
        fh.write(svg)
    tmp = os.path.join(QA, "_preview.svg")
    with open(tmp, "w") as fh:
        fh.write(preview_svg(foil))
    render(tmp, os.path.join(BUILD, "SEAL.png"), 330)
    render(tmp, os.path.join(BUILD, "SEAL@3x.png"), 990)
    render(tmp, os.path.join(BUILD, "SEAL-83.png"), 83)
    os.remove(tmp)
    render(OUT_SVG, os.path.join(BUILD, "SEAL-print.png"), 810)
    tmpm = os.path.join(QA, "_mock.svg")
    with open(tmpm, "w") as fh:
        fh.write(preview_svg(foil, mock=True, ground=T.BOARD, pad=24, shadow=True))
    render(tmpm, os.path.join(BUILD, "SEAL-mock.png"), 1134)
    render(tmpm, os.path.join(BUILD, "SEAL-mock-small.png"), 142)
    os.remove(tmpm)
    crops(foil, sal)
    rep = qa(foil, sal, info, svg)
    flags_png(foil, rep)
    rep.pop("_flags", None)
    with open(os.path.join(QA, "SEAL-qa.json"), "w") as fh:
        json.dump(rep, fh, indent=1, default=str)
    print(f"built + checked in {time.time() - t0:.1f} s")
    print(row(rep))
    print("facts:", json.dumps(rep["facts"]))
    ok = all(rep[c]["ok"] for c in ("1_strk", "4_pal", "8_safe", "12_gaps", "17_svg", "25_rndr", "copy_J2"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
