"""Build the HEADWATERS tuck box (brief §H.20, §D.2, §B.1) and check it.

    .venv/bin/python -m tuck.build_tuck            (run from the project root)
    .venv/bin/python -m tuck.build_tuck --no-mock  (print files + QA only)

Print files (flat Lion Gold foil, emboss as a non-printing tooling plate, all
type outlined, no gradients / filters / <text>):
    tuck/TUCK-FRONT.svg      769 x 1069 front panel
    tuck/TUCK-BACK.svg       769 x 1069 back panel (derived from art/BACK.py at build time)
    tuck/TUCK-SIDE-A.svg     225 x 1069  HEADWATERS · LONG MAY IT FLOW
    tuck/TUCK-SIDE-B.svg     225 x 1069  72 degrees + the acknowledgment (HOLD for review)
    tuck/TUCK-TOP.svg        769 x 225   SAN MARVELOUS + the diving pig
    tuck/TUCK-BOTTOM.svg     769 x 225   the ghost gambusia
    tuck/TUCK-FLAT.svg       everything on a STANDARD reverse-tuck dieline (replace
                             with the printer's): plates board / emboss / foil / dieline
Renders (build/tuck/):
    TUCK-FRONT.png / TUCK-BACK.png (flat foil, 1:1), TUCK-FRONT@3x.png, TUCK-FRONT-192.png (25 %),
    TUCK-FRONT-mock.png, TUCK-BACK-mock.png (FOIL_PREVIEW gradient + subtle emboss, mock-ups only),
    TUCK-FLAT.png, TUCK-PRESENTATION.png, TUCK-SIDES.png, TUCK-ENDS.png
QA: build/tuck/qa/TUCK-qa.json (+ printed rows), flags in build/tuck/qa/TUCK-<piece>-flags.png
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
import shapely
import shapely.ops

from deck import tokens as T
from deck.motifs import core as C

from tuck import _tuck_common as K

QA_DIR = K.OUT / "qa"
NS = "{http://www.w3.org/2000/svg}"
BANNED = {"text", "tspan", "textPath", "image", "filter", "linearGradient", "radialGradient", "pattern", "mask",
          "use", "symbol", "marker", "switch", "style", "a", "foreignObject"}
SAFE = T.SAFE                     # 37.5 px from every fold / cut for type and critical art
BORDER_MIN = 25.0                 # decorative border (rules, corner roundels) may sit this close to a fold (2.1 mm)

COPY = {  # §J.2 verbatim
    "HEADWATERS", "PLAYING CARDS OF THE SAN MARCOS SPRINGS", "NAMED FOR ST. MARK · 1689", "SAN MARCOS · TEXAS",
    "NUMQUAM DEFICIT", "HEADWATERS · LONG MAY IT FLOW", "SEVENTY-TWO DEGREES · EVERY DAY OF THE YEAR",
    "THE SPRINGS HAVE BEEN CARED FOR BY INDIGENOUS PEOPLES FOR MORE THAN 12,000 YEARS", "SAN MARVELOUS",
    "GAMBUSIA GEORGEI · LAST SEEN 1983"}


# =============================================================================
# build
# =============================================================================
def build_all():
    from tuck import _tuck_front as TF, _tuck_back as TB, _tuck_panels as TP, _tuck_flat as FL
    t0 = time.time()
    front = TF.build()
    back = TB.build()
    panels = TP.build()
    flat = FL.build(front, back, panels)
    print(f"built in {time.time() - t0:.1f} s")
    return dict(front=front, back=back, panels=panels, flat=flat)


def write_svgs(b):
    from tuck import _tuck_front as TF, _tuck_back as TB, _tuck_panels as TP, _tuck_flat as FL
    out = {}
    out["FRONT"] = K.write(K.TUCK / "TUCK-FRONT.svg", TF.svg(b["front"]))
    out["BACK"] = K.write(K.TUCK / "TUCK-BACK.svg", TB.svg(b["back"]))
    for key, name, w, h in (("side_a", "SIDE-A", K.DEPTH, K.PH), ("side_b", "SIDE-B", K.DEPTH, K.PH),
                            ("top", "TOP", K.PW, K.DEPTH), ("bottom", "BOTTOM", K.PW, K.DEPTH)):
        die = ""
        if key == "side_b":
            ax0, ay0, ax1, ay1 = b["panels"]["ack_bb"]
            note = TP.hold_note_d(17.0, K.PH / 2)                     # in the margin, clear of the art
            from inkkit import geom as G
            die = (f'<path d="{G.rect_d(ax0 - 6, ay0 - 8, ax1 - ax0 + 12, ay1 - ay0 + 16)}" fill="none" '
                   f'stroke="{K.DIE_REG}" stroke-width="{T.HAIRLINE}" stroke-dasharray="6 5" data-note="hold"/>'
                   f'<path d="{note}" fill="{K.DIE_REG}" data-note="HOLD (non-printing)"/>')
        out[name] = K.write(K.TUCK / f"TUCK-{name}.svg", TP.panel_svg(name, b["panels"][key], w, h, dieline=die))
    out["FLAT"] = K.write(K.TUCK / "TUCK-FLAT.svg", FL.svg(b["flat"]))
    return out


def print_view(svg_path: Path, *, dieline=True) -> str:
    """The print SVG without its non-printing plates (emboss hidden; with
    ``dieline=False`` the dieline / notes too), for renders."""
    s = svg_path.read_text()
    s = re.sub(r'(<g id="emboss"[^>]*?)>', r'\1 style="display:none">', s, count=1)
    if not dieline:
        s = re.sub(r'(<g id="dieline"[^>]*?)>', r'\1 style="display:none">', s, count=1)
    return s


def render_all(b, svgs, mock=True):
    from tuck import _tuck_mock as MK
    K.OUT.mkdir(parents=True, exist_ok=True)
    tmp = K.OUT / ".tmp"
    tmp.mkdir(exist_ok=True)
    for name in ("FRONT", "BACK"):
        pv = K.write(tmp / f"{name}-print.svg", print_view(svgs[name]))
        K.render(pv, K.OUT / f"TUCK-{name}.png", 769)
        K.render(pv, K.OUT / f"TUCK-{name}@3x.png", 769 * 3)
        K.render(pv, K.OUT / f"TUCK-{name}-192.png", 192)
    # sides and ends, flat foil, as strips
    for name, w in (("SIDE-A", 225), ("SIDE-B", 225), ("TOP", 769), ("BOTTOM", 769)):
        pv = K.write(tmp / f"{name}-print.svg", print_view(svgs[name]))
        K.render(pv, tmp / f"{name}.png", w)
        K.render(pv, K.OUT / f"TUCK-{name}@3x.png", w * 3)
    subprocess.run(["magick", str(tmp / "SIDE-A.png"), str(tmp / "SIDE-B.png"), "-background", "#E6E0D3", "-splice",
                    "24x0", "+append", "-bordercolor", "#E6E0D3", "-border", "24", str(K.OUT / "TUCK-SIDES.png")],
                   check=True)
    subprocess.run(["magick", str(tmp / "TOP.png"), str(tmp / "BOTTOM.png"), "-background", "#E6E0D3", "-splice",
                    "0x24", "-append", "-bordercolor", "#E6E0D3", "-border", "24", str(K.OUT / "TUCK-ENDS.png")],
                   check=True)
    fp = K.write(tmp / "FLAT-print.svg", print_view(svgs["FLAT"]))
    K.render(fp, K.OUT / "TUCK-FLAT.png", 2138 + 75)
    if not mock:
        return
    fm = K.write(tmp / "front-mock.svg", MK.panel_mock(b["front"], K.PW, K.PH, pad=40))
    K.render(fm, K.OUT / "TUCK-FRONT-mock.png", (769 + 80) * 2)
    bm = K.write(tmp / "back-mock.svg", MK.panel_mock(b["back"], K.PW, K.PH, pad=40))
    K.render(bm, K.OUT / "TUCK-BACK-mock.png", (769 + 80) * 2)
    stale = [r for r in MK.mock_inputs() if not r["fresh"]]
    for r in stale:
        print(f"!! STALE mock input {r['png']} ({r.get('png_mtime')}) is older than art/{r.get('newest_src')} "
              f"({r.get('src_mtime')}): run `python -m deck.build {r['card']}` and rebuild the tuck")
    pr = K.write(tmp / "presentation.svg", MK.presentation(b["front"], b["back"], b["panels"]))
    K.render(pr, K.OUT / "TUCK-PRESENTATION.png", 2600)
    K.render(pr, K.OUT / "TUCK-PRESENTATION-small.png", 1300)


# =============================================================================
# QA
# =============================================================================
def _plates(svg_text):
    root = ET.fromstring(svg_text)
    return root, {g.get("id"): g for g in root if g.tag == NS + "g"}


def _foil_only(svg_text) -> str:
    """The foil plate alone, as a one-layer SVG the deck QA geometry reads
    (layer id 'gold')."""
    root, pl = _plates(svg_text)
    inner = "".join(ET.tostring(ch, encoding="unicode") for ch in pl["foil"])
    inner = inner.replace("ns0:", "").replace(' xmlns:ns0="http://www.w3.org/2000/svg"', "")
    vb = root.get("viewBox")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}"><g id="gold">{inner}</g></svg>')


def foil_gaps(shape, *, sep=3.0, par=4.2, ko=2.5, run_min=12.0, parallel=True, type_shape=None) -> list[dict]:
    """§I.12 on the FOIL AS STAMPED (the exact union of every mark, what the
    foil die is cut from): marks that touch fuse into one piece, so a
    junction of three strokes is one piece, as it is on the board.
      * separate foil pieces: >= ``sep`` (3.0) apart; where they run alongside
        each other for >= 12 px, >= ``par`` (4.2) (§I.12 parallel strokes);
      * enclosed board (holes in the foil): at least ``ko`` (2.5) wide — a
        knockout line (the wordmark's inline groove, a ring's eye);
      * foil no thinner than HAIRLINE (1.6, the foil minimum)."""
    geoms = [g for g in getattr(shape, "geoms", [shape]) if g.area > 0.05]
    out = []
    arr = np.array(geoms, dtype=object)
    tree = shapely.STRtree(arr)
    pairs = tree.query(arr, predicate="dwithin", distance=par)
    for i, j in zip(*pairs):
        if i >= j:
            continue
        a, b = geoms[i], geoms[j]
        d = float(shapely.distance(a, b))
        if d < 0.08:
            continue
        rule = need = None
        if d < sep - 0.08:
            rule, need = "separate foil pieces", sep
        elif parallel and d < par - 0.08:
            # the run: the ONE patch of a lying within 4.2 of b around the closest approach, and the
            # same for b, not every place the two big pieces happen to come near each other.  Two pieces
            # run ALONGSIDE each other only as far as BOTH do, so the run is the shorter patch -- which
            # also makes the verdict independent of the (arbitrary) order of the union's pieces: a ring
            # tangent to a rule (the side medallions vs the outer RULE, 3.1 px, a §I.12 approach) gives
            # 13.1 px measured along the rule but 11.4 along the ring, and used to pass or fail by order.
            def _run(p, q):
                pn, _ = shapely.ops.nearest_points(p, q)
                near_p = p.intersection(q.buffer(par + 0.1, quad_segs=4))
                patches = [g for g in getattr(near_p, "geoms", [near_p]) if g.distance(pn) < 0.3]
                near = shapely.union_all(patches) if patches else near_p
                if near.is_empty:
                    return 0.0
                rr = near.minimum_rotated_rectangle
                if rr.geom_type != "Polygon":
                    return 0.0
                xy = np.asarray(rr.exterior.coords)
                return max(np.linalg.norm(xy[1] - xy[0]), np.linalg.norm(xy[2] - xy[1]))
            run = min(_run(a, b), _run(b, a))
            if run >= run_min:
                rule, need = f"parallel foil (run {run:.0f} px)", par
        if rule:
            p1, p2 = shapely.ops.nearest_points(a, b)
            out.append({"at": [round((p1.x + p2.x) / 2, 1), round((p1.y + p2.y) / 2, 1)], "gap": round(d, 2),
                        "need": need, "rule": rule})
    for g in geoms:
        mic = shapely.maximum_inscribed_circle(g, 0.02)
        if 2 * mic.length < T.HAIRLINE - 0.08:
            c = mic.coords[0]
            out.append({"at": [round(c[0], 1), round(c[1], 1)], "gap": round(2 * mic.length, 2), "need": T.HAIRLINE,
                        "rule": "foil thinner than HAIRLINE"})
        for ring in g.interiors:
            hole = shapely.Polygon(ring)
            if hole.area < 0.3:
                c = hole.representative_point()
                out.append({"at": [round(c.x, 1), round(c.y, 1)], "gap": 0.0, "need": ko,
                            "rule": "pinhole in the foil"})
                continue
            hm = shapely.maximum_inscribed_circle(hole, 0.02)
            if 2 * hm.length < ko - 0.08:
                c = hm.coords[0]
                counter = type_shape is not None and type_shape.contains(hole)
                out.append({"at": [round(c[0], 1), round(c[1], 1)], "gap": round(2 * hm.length, 2), "need": ko,
                            "rule": "type counter (warn)" if counter else "enclosed board too narrow (knockout)"})
    out.sort(key=lambda r: r["gap"])
    return out


def tight_board(frag: C.Frag, min_gap=4.2, cluster=10.0) -> list[dict]:
    """Raster warning (!): board narrower than 4.2 px between foil that is
    connected elsewhere (a close approach within one piece), clusters of at
    least ``cluster`` px² — look at each (V-junctions always show a little)."""
    from deck.motifs.forms import tight_spots
    from scipy import ndimage
    ts = tight_spots(frag, min_gap, res=0.35)
    mask = ts["mask"]
    th = K.type_hull(frag)
    if th is not None:                     # the inline groove and letter counters are knockouts by design
        x0_, y0_ = ts["extent"][:2]
        ys_, xs_ = np.nonzero(mask)
        if len(xs_):
            inside = shapely.contains_xy(th.buffer(1.0), x0_ + (xs_ + 0.5) * ts["res"], y0_ + (ys_ + 0.5) * ts["res"])
            mask = mask.copy()
            mask[ys_[inside], xs_[inside]] = False
    lab, n = ndimage.label(mask)
    out = []
    x0, y0 = ts["extent"][:2]
    for k in range(1, n + 1):
        ys, xs = np.nonzero(lab == k)
        area = len(xs) * ts["res"] ** 2
        if area >= cluster:
            out.append({"at": [round(x0 + xs.mean() * ts["res"], 1), round(y0 + ys.mean() * ts["res"], 1)],
                        "area": round(area, 1)})
    out.sort(key=lambda r: -r["area"])
    return out


def qa_piece(name, svg_path: Path, frag: C.Frag | None, panel_wh, *, flat=False, extra_solids=None) -> dict:
    from deck import qa as DQ
    s = svg_path.read_text()
    r = {"piece": name}
    root, pl = _plates(s)
    # 17 structure: banned tags, plates present and in order
    tags = {el.tag.replace(NS, "") for el in root.iter()}
    bad = sorted(tags & BANNED)
    need = ["board", "emboss", "foil"] + (["dieline"] if flat else [])
    order = [g.get("id") for g in root if g.tag == NS + "g"]
    ok_order = [x for x in order if x in need] == need
    r["17_svg"] = {"ok": not bad and ok_order, "banned": bad, "plates": order}
    # 1 stroke widths (foil plate)
    widths = set()
    for el in pl["foil"].iter():
        w = el.get("stroke-width")
        if w is not None and (el.get("stroke") not in (None, "none")):
            widths.add(round(float(w), 3))
    illegal = sorted(w for w in widths if w not in T.LEGAL_STROKES)
    tf = [el.get("transform") for el in root.iter() if el.get("transform")]
    r["1_strk"] = {"ok": not illegal and not tf, "widths": sorted(widths), "illegal": illegal,
                   "transforms": len(tf)}
    # 4 palette: one foil, flat; board = Deep Hole; nothing board-coloured painted in the foil plate (§I.24 analogue)
    cols = set()
    for el in pl["foil"].iter():
        for k in ("fill", "stroke"):
            v = el.get(k)
            if v and v != "none":
                cols.add(v.lower())
    bcols = {el.get("fill", "").lower() for el in pl["board"].iter() if el.get("fill")}
    r["4_pal"] = {"ok": cols <= {T.FOIL.lower()} and bcols <= {T.BOARD.lower()}, "foil_colours": sorted(cols),
                  "board": sorted(bcols)}
    # 12 gaps on the foil as stamped (union), + the wordmark's solid bridges (deck QA on its fills)
    t0 = time.time()
    if frag is not None:
        gaps = foil_gaps(frag.shape(), parallel=(name != "BACK"), type_shape=K.type_hull(frag))
        warn_counters = [g for g in gaps if "warn" in g["rule"]]
        gaps = [g for g in gaps if "warn" not in g["rule"]]
        if extra_solids is not None:
            sp = DQ.card_geometry(_foil_only(K.svg_doc(K.PW, K.PH, foil=K.foil_svg(extra_solids))))
            gaps += [g for g in DQ.vector_gaps(sp) if "bridge" in g["rule"] or "sliver" in g["rule"]
                     or "hole" in g["rule"]]
        tb = tight_board(frag) if name != "BACK" else []
        r["12_gaps"] = {"ok": not gaps, "n": len(gaps), "worst": gaps[:12], "s": round(time.time() - t0, 1),
                        "raster_warn": len(tb), "raster_worst": tb[:12],
                        "type_counters_warn": [(g["gap"], g["at"]) for g in warn_counters]}
    else:
        gaps = []
        r["12_gaps"] = {"ok": None, "n": 0, "worst": [], "note": "flat = the panels above, placed rigidly"}
    # 8 safe zone (panels): type >= 37.5 from every edge; any foil >= 30 (the border rule)
    if frag is not None and panel_wh:
        w, h = panel_wh
        inner = shapely.box(SAFE, SAFE, w - SAFE, h - SAFE)
        border_zone = shapely.box(BORDER_MIN, BORDER_MIN, w - BORDER_MIN, h - BORDER_MIN)
        allg = frag.shape()
        typ = C.Frag([m for m in frag.marks if m.role in ("type", "wordmark")]).shape()
        out_type = typ.difference(inner).area if not typ.is_empty else 0.0
        out_any = allg.difference(border_zone).area
        x0, y0, x1, y1 = allg.bounds
        r["8_safe"] = {"ok": out_type < 0.01 and out_any < 0.01, "type_outside_37.5_px2": round(out_type, 3),
                       "foil_outside_25_px2": round(out_any, 3),
                       "min_margin": round(min(x0, y0, w - x1, h - y1), 2)}
    # 25 rsvg vs resvg (print view)
    pv = K.OUT / ".tmp" / f"qa-{name}.svg"
    K.write(pv, print_view(svg_path, dieline=False))
    # 1:1 for the big panels and the flat; the narrow side / end panels at 3x (a 225 px strip is mostly edge
    # pixels, where the two rasterisers' antialiasing differs by design)
    wpx = int(2138 + 75) if flat else (769 if panel_wh and panel_wh[0] >= 700 and panel_wh[1] >= 700
                                       else int(3 * panel_wh[0]))
    try:
        a = DQ._rsvg(pv.read_text(), wpx).astype(int)
        bimg = DQ._resvg(str(pv), wpx).astype(int)
        hh = min(a.shape[0], bimg.shape[0])
        diff = np.abs(a[:hh] - bimg[:hh]).max(axis=2) > 40
        frac = float(diff.mean())
        r["25_rndr"] = {"ok": frac < DQ.RENDER_DIFF_MAX, "diff_frac": round(frac, 5)}
    except Exception as e:  # noqa: BLE001
        r["25_rndr"] = {"ok": False, "error": str(e)[:200]}
    # raster flags: the gaps overlay
    if gaps:
        _flags(name, pv, gaps)
    return r


def _flags(name, svg_path, gaps):
    s = svg_path.read_text()
    marks = "".join(f'<circle cx="{g["at"][0]}" cy="{g["at"][1]}" r="9" fill="none" stroke="#FF2020" '
                    f'stroke-width="2"/>' for g in gaps)
    s = s.replace("</svg>", f"<g>{marks}</g></svg>")
    p = K.write(QA_DIR / f"TUCK-{name}-flags.svg", s)
    K.render(p, QA_DIR / f"TUCK-{name}-flags.png", 1538)


def qa_copy():
    from tuck import _tuck_front as TF, _tuck_panels as TP
    used = {TF.KICKER, "HEADWATERS", TF.SUBLINE, TF.MOTTO, TF.PLACE, TP.SIDE_A, TP.SIDE_B1,
            " ".join(TP.SIDE_B_ACK), TP.TOP_LINE, TP.BOTTOM_LINE}
    return {"ok": used <= COPY, "not_in_J2": sorted(used - COPY)}


def run_qa(b, svgs):
    QA_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    p = b["panels"]
    for name, frag, wh, flat in (("FRONT", b["front"]["foil"], (K.PW, K.PH), False),
                                 ("BACK", b["back"]["foil"], (K.PW, K.PH), False),
                                 ("SIDE-A", p["side_a"], (K.DEPTH, K.PH), False),
                                 ("SIDE-B", p["side_b"], (K.DEPTH, K.PH), False),
                                 ("TOP", p["top"], (K.PW, K.DEPTH), False),
                                 ("BOTTOM", p["bottom"], (K.PW, K.DEPTH), False),
                                 ("FLAT", None, None, True)):
        ex = b["front"]["parts"]["wordmark"]["fill"] if name == "FRONT" else None
        rows.append(qa_piece(name, svgs[name], frag, wh, flat=flat, extra_solids=ex))
    from tuck import _tuck_mock as MK
    mi = MK.mock_inputs()
    rep = {"pieces": rows, "copy_J2": qa_copy(), "mock_inputs": {"ok": all(r["fresh"] for r in mi), "cards": mi},
           "motif_check": {k: C.check(v)[:5] for k, v in (
        ("front", b["front"]["foil"]), ("back", b["back"]["foil"]))}}
    (QA_DIR / "TUCK-qa.json").write_text(json.dumps(rep, indent=1, default=str))
    sym = lambda v: "✓" if v is True else ("✗" if v is False else "·")
    cols = ["1_strk", "4_pal", "8_safe", "12_gaps", "17_svg", "25_rndr"]
    print(f"{'piece':8} " + " ".join(f"{c:>8}" for c in cols) + "   detail")
    for r in rows:
        det = []
        g12 = r.get("12_gaps", {})
        if g12.get("n"):
            det.append(f"{g12['n']} gaps, worst {g12['worst'][0]['gap']} "
                       f"({g12['worst'][0]['rule']}) at {g12['worst'][0]['at']}")
        if g12.get("raster_warn"):
            det.append(f"! {g12['raster_warn']} tight-board clusters")
        if "8_safe" in r:
            det.append(f"margin {r['8_safe']['min_margin']}")
        if "25_rndr" in r:
            det.append(f"rsvg/resvg {r['25_rndr'].get('diff_frac')}")
        print(f"{r['piece']:8} " + " ".join(f"{sym(r.get(c, {}).get('ok')):>8}" for c in cols) + "   " + "; ".join(det))
    print(f"copy §J.2 verbatim: {sym(rep['copy_J2']['ok'])} {rep['copy_J2']['not_in_J2'] or ''}")
    print("mock inputs fresh (presentation embeds): " + sym(rep["mock_inputs"]["ok"]) + "  " + "; ".join(
        f"{r['card']} {r.get('png_mtime')} (src {r.get('newest_src')} {r.get('src_mtime')})" for r in mi))
    return rep


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-mock", action="store_true")
    ap.add_argument("--no-qa", action="store_true")
    a = ap.parse_args(argv)
    b = build_all()
    svgs = write_svgs(b)
    for s in svgs.values():
        assert "<text" not in s.read_text()
    render_all(b, svgs, mock=not a.no_mock)
    if not a.no_qa:
        run_qa(b, svgs)


if __name__ == "__main__":
    main()
