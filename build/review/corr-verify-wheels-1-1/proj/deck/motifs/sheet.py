"""Specimen sheet for the geometric ornament library (§G).

    .venv/bin/python -m deck.motifs.sheet                 # both sheets, from the project root
    .venv/bin/python -m deck.motifs.sheet figurative      # only build/motifs/sheet-figurative.png
    .venv/bin/python -m deck.motifs.sheet geometric       # only the geometric sheet

Writes
  build/motifs/sheet-geometric.png   every motif at real use size (1 px = 1
                                     card px, i.e. 300 ppi), line-on-Limestone
                                     and reversed out of a jade flood, plus 3×
                                     zoom crops of the delicate ones
  build/motifs/cells/*.svg           the per-cell SVGs (layer groups
                                     paper/jade/red/gold/ink, no transforms)
  build/motifs/back-test*.png        a back-scale integration test of the
                                     frame/lens/rosette motifs in knockout mode
                                     (NOT the back design) at 750 and 188 px,
                                     on Limestone and on white, with coverage.
"""
from __future__ import annotations

import math
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from shapely.geometry import box

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from inkkit import geom as G  # noqa: E402

from deck import tokens as T  # noqa: E402
from deck.motifs import core as C  # noqa: E402
from deck.motifs import geometric as M  # noqa: E402

OUT = ROOT / "build" / "motifs"
CELLS = OUT / "cells"
PAGE_BG = (226, 223, 215)
LABEL = (40, 40, 40)
SUB = (110, 110, 110)
PAD = 14                       # px around a motif inside its cell


# ---------------------------------------------------------------------------
# SVG + render helpers
# ---------------------------------------------------------------------------
def layered_svg(f: C.Frag, view, *, ground: str | None = T.PAPER, flood: str | None = None,
                flood_d: str | None = None, under=()) -> str:
    """A print-layered SVG: <g id> groups paper, jade, red, gold, ink (§K).
    ``flood`` reverses the motif out of that colour (geometric knockout).
    ``under`` = [(d, colour)] context shapes painted first, in the paper
    group (specimen previews only: the A♠ spade, the tuck board, the seal)."""
    x0, y0, x1, y1 = view
    W, H = x1 - x0, y1 - y0
    groups = {k: [] for k in T.LAYERS}
    if ground:
        groups["paper"].append(f'<path d="M{x0} {y0}h{W}v{H}h{-W}z" fill="{ground}"/>')
    for d_u, col_u in under:
        groups["paper"].append(f'<path d="{d_u}" fill="{col_u}"/>')
    if flood:
        solid = flood_d or f"M{x0} {y0}h{W}v{H}h{-W}z"
        ko = C.knockout(solid, f)
        groups[C.LAYER_OF[flood]].append(f'<path d="{ko}" fill="{flood}"/>')
    else:
        for lay, s in f.layers().items():
            groups[lay].append(s)
    body = "".join(f'<g id="{k}">{"".join(v)}</g>' for k, v in groups.items())
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.2f}" height="{H:.2f}" '
            f'viewBox="{x0:.2f} {y0:.2f} {W:.2f} {H:.2f}">{body}</svg>')


def render(svg_path: Path, png_path: Path, zoom: float = 1.0, width: int | None = None) -> Image.Image:
    args = ["rsvg-convert", str(svg_path), "-o", str(png_path)]
    args[1:1] = ["-w", str(width)] if width else ["-z", str(zoom)]
    subprocess.run(args, check=True)
    return Image.open(png_path).convert("RGB")


def font(size: int, medium: bool = False):
    p = T.FONT_MICRO_MEDIUM if medium else T.FONT_INDEX
    return ImageFont.truetype(str(p), size)


# ---------------------------------------------------------------------------
# the specimens (each built at its real use size, around its own origin)
# ---------------------------------------------------------------------------
def specimens():
    """[(title, brief ref, note, frag, zoom_box or None)]; zoom_box in the
    frag's own coordinates for the 3× crop."""
    S = []

    def add(title, ref, note, f, zoom=None, view=None):
        S.append(dict(title=title, ref=ref, note=note, frag=f, zoom=zoom, view=view))

    ros = M.source_rosette(0, 0, 130)
    add("Source Rosette — back", "§G.1", "R130: crater r20 · rings 30/39/50 · 24 bubbles Ø7 · pinwheel 72–104 twisted 25° · wave ring cw",
        ros, zoom=(-20, -135, 135, 5))
    add("Rosette — medium", "§G.1", "R90 (tuck scale), C_N", M.source_rosette(0, 0, 90))
    add("Rosette — small, D2", "§G.1 / H.14", "R40, straight ribs, MEDIUM (Ace of Hearts knockout)",
        M.source_rosette(0, 0, 40, twist=False, w=T.MEDIUM), zoom=(-45, -45, 45, 45))
    add("Rosette — tiny", "§G.1 / H.1", "R16 jewel / finial", M.source_rosette(0, 0, 16), zoom=(-20, -20, 20, 20))

    band = M.running_wave_d2(0, 0, 290, gap=34) + M.fault_plinth(0, 0, 60, hatch_step=0)
    add("Running wave — D2 band", "§G.7 / H.19", "mirrored at the axis, flowing outward; fault-step plinth (2 treads)",
        band, zoom=(-100, -26, 60, 6))
    add("Running wave — ring", "§G.7", "cw (C_n) and mirrored (D2, meets at 3 & 9 o'clock)",
        M.running_wave_ring(0, 0, 60, n=12) + M.running_wave_ring(180, 0, 60, mirrored=True, n=16),
        zoom=(-40, -90, 40, -40))
    add("Ripple rings", "§G.8", "gaps ×1.3 outward: circles · offset ellipse arcs · similar ellipses",
        M.ripple_rings(0, 0, 14, 7) + M.ripple_rings(110, 0, 34, 7, ry_ratio=0.25, arc=(0, 180))
        + M.ripple_rings(250, 0, 60, 30, n=3, ratio=1.0, ry_ratio=8 / 60, mode="similar", arc=(0, 180)))
    add("Bubble beading", "§G.9", "×1.2 toward the rise; dots < Ø5.1, rings above",
        M.bubble_beading((0, 60), (0, -40), 3, n=7) + M.bubble_beading((30, 60), (100, -40), 3.5, n=7)
        + C.bubble_row((130, 60), (130, -40), C.bubble_sizes(5.5, 6, 1.12), style="ring")
        + C.bubble_triad(170, 10, -45, (4.2, 6.3, 8.4)) + C.bubble_triad(200, 10, -45, (6.3, 10.5, 6.3), style="ring"))
    add("Fault-step", "§G.10", "one right-angle step, rise 4.5×w; double; stepped plinth",
        M.fault_step(0, 120, 0) + M.fault_step(0, 120, 30, double=6.3)
        + M.fault_plinth(200, 40, 60, hatch_step=0) + M.fault_plinth(300, 40, 80, steps=2, hatch_step=None))
    reg = box(0, 0, 220, 150)
    add("Strata bands + fault jog", "§G.11", "courses 12/19, thin ones hatched 45°; courses right of the fault drop one course",
        C.stroke(G.rect_d(0, 0, 220, 150), style="rule") + M.strata(reg, fault=((80, 150), (150, 0))),
        zoom=(40, 0, 180, 70))
    add("Karst voids", "§G.12", "staggered grid Ø6/10/16, largest with crescent inner offset",
        C.stroke(G.rect_d(0, 0, 220, 150), style="rule") + M.karst_voids(box(0, 0, 220, 150)), zoom=(0, 0, 110, 75))
    st = C.Frag()
    for k, (L, W) in enumerate([(40, 14), (52, 17), (64, 20), (52, 17), (40, 14)]):
        st += M.stalactite(k * 28, 0, L, W, hatch_side="left" if k < 2 else ("right" if k > 2 else "left"))
    add("Stalactite points", "§G.13", "kite, 3 growth arcs on one half, the other half hatched", st, zoom=(-14, -4, 70, 70))
    add("Drip fringe", "§G.14", "sine envelope, Ø6.3 terminals", M.drip_fringe(0, 220, 0))
    shield = "M0 0H120V70C120 110 90 135 60 145C30 135 0 110 0 70Z"
    add("Scale lattice", "§G.16", "row step 0.6 r, shingled, clipped (QH bodice, KH trim)",
        C.stroke(shield, style="rule") + M.scale_lattice(shield, 10), zoom=(0, 0, 70, 60))
    add("Cypress-knee crenellation", "§G.17", "heights .65/.8/1/.8/.65, half-hatched",
        M.knee_crenellation(0, 240, 0, h=50), zoom=(60, -60, 180, 6))
    add("Comb spray + cone", "§G.18", "vesica tick envelope; round cone = circle + 4 scale arcs",
        M.comb_spray("M0 60 C 40 30 100 10 170 15", cone=11) + M.comb_spray("M190 70 L 260 -10")
        + M.comb_spray("M280 60 A 90 90 0 0 1 350 -20"), zoom=(120, -5, 190, 40))
    add("Reed ladder", "§G.19 / H.19", "rails 16, rungs 26, node ellipse every 4th; medallion Ø26 / Ø40",
        M.reed_ladder((0, 0), (0, 260)) + M.reed_node_medallion(50, 130, 26, rot=90)
        + M.reed_node_medallion(100, 130, 40) + M.reed_node(160, 130), zoom=(-14, 100, 130, 160))
    add("Ashlar courses", "§G.20", "running bond, 3 px chamfers, clipped",
        C.stroke(G.rect_d(0, 0, 200, 120), style="rule") + M.ashlar(box(0, 0, 200, 120)))
    add("Arcade", "§G.21", "semicircle on jambs + keystone; with extrados ring (default) / single line",
        M.arcade(0, 260, 0, span=30, jamb=14) + M.arcade(0, 260, 60, span=30, jamb=14, ring=None),
        zoom=(0, -45, 100, 5))
    add("Rowel star · compass", "§G.22 / H.16", "split lozenges, one half hatched; (1, .6) compass; solid rowel",
        M.rowel_star(0, 0, 45) + M.rowel_star(130, 0, 60, lengths=(1.0, 0.6), hub=10)
        + M.rowel_star(215, 0, 16, hub=4, solid=True), zoom=(-50, -50, 50, 50))
    add("Stepping-stone chain", "§G.23", "lozenges between a double rule, larger centre stone (rails break 4.2)",
        M.stepping_stones(0, 300, 0))
    add("Vent roundel", "§G.27", "Ø56, inner Ø16, 12 straight ribs", M.vent_roundel(0, 0, 56), zoom=(-32, -32, 32, 32))
    add("Festoon catenary", "§G.28", "catenaries, Ø6.3 bulbs at low points and joins",
        M.festoon([(0, 0), (110, 0), (220, 12)], sag=22))
    add("Pearl beading", "§G.29", "graduated, largest at the centre",
        M.pearl_beading("M0 40 A 130 130 0 0 1 220 40"))
    strat = M.strata(box(0, 60, 140, 140))
    cond = M.conduit("M70 170 L70 0", 16, d0=3, n=7)
    add("Conduit", "§G.30", "rails 16 apart, bubbles ×1.2 rising; what it crosses breaks 4 px",
        M.conduit_break(C.stroke(G.rect_d(0, 60, 140, 80), style="rule") + strat, cond) + cond,
        zoom=(30, 40, 110, 110))
    add("Tooled scroll", "§G.31", "eye volutes alternating, S-links branch tangentially, one leaf per turn (Ford cuffs only)",
        M.tooled_scroll(0, 300, 0, height=36) + M.volute(340, 0, 14), zoom=(0, -22, 110, 22))
    # core helpers
    leaf = C.vesica_d((0, 60), (0, -60), 44)
    s1 = "M-60 -40 C -20 -40 20 40 60 40"
    s2 = "M-60 40 C -20 40 20 -40 60 -40"
    il = C.interlace(C.stroke(s2), C.stroke(s1)).translate(170, 0)
    add("Core: split leaf · interlace · terminals", "§B.2", "half-hatch perpendicular to the midrib, butt on the centrelines; under-stroke breaks 4.2 clear; Ø6.3 terminals",
        C.stroke(leaf, style="point") + C.stroke("M0 -60L0 60", style="point") + C.half_hatch(leaf, "left", "perp")
        + il + C.stroke("M280 -40 C 330 -40 300 40 350 40", terminals="both"),
        zoom=(100, -50, 240, 50))
    return S


# ---------------------------------------------------------------------------
# sheet assembly
# ---------------------------------------------------------------------------
def build_cell(i, spec, prefix=""):
    f = spec["frag"]
    x0, y0, x1, y1 = spec["view"] if spec.get("view") else f.bbox()
    view = (math.floor(x0 - PAD), math.floor(y0 - PAD), math.ceil(x1 + PAD), math.ceil(y1 + PAD))
    tag = f"{prefix}{i:02d}"
    out = {}
    line_kw = dict(ground=spec.get("ground", T.PAPER), under=spec.get("under", ()))
    for mode, kw in (("line", line_kw), ("ko", dict(ground=T.PAPER, flood=T.JADE))):
        svg = layered_svg(f, view, **kw)
        p = CELLS / f"{tag}-{mode}.svg"
        p.write_text(svg)
        out[mode] = render(p, CELLS / f"{tag}-{mode}.png", 1.0)
        if spec["zoom"]:
            zx0, zy0, zx1, zy1 = spec["zoom"]
            zv = (zx0, zy0, zx1, zy1)
            ground = T.PAPER
            zsvg = layered_svg(f, zv, **kw) if mode == "line" else layered_svg(
                f, zv, ground=ground, flood=T.JADE,
                flood_d=f"M{view[0]} {view[1]}H{view[2]}V{view[3]}H{view[0]}Z")
            zp = CELLS / f"{tag}-{mode}-zoom.svg"
            zp.write_text(zsvg)
            out[mode + "_zoom"] = render(zp, CELLS / f"{tag}-{mode}-zoom.png", 3.0)
    return out


def compose(specs, imgs, width=3000, title="HEADWATERS · ornament library · geometric vocabulary (§G)",
            sub=None):
    ft, fs = font(30, medium=True), font(20)
    gap, head = 36, 64
    # measure cells: [line | ko] then zooms below
    blocks = []
    for spec, im in zip(specs, imgs):
        a, b = im["line"], im["ko"]
        w = a.width + b.width + 12
        h = max(a.height, b.height)
        zooms = []
        if "line_zoom" in im:
            zooms = [im["line_zoom"], im["ko_zoom"]]
        zw = sum(z.width for z in zooms) + (12 if zooms else 0)
        zh = max((z.height for z in zooms), default=0)
        blocks.append((spec, a, b, zooms, max(w, zw, 420), head + h + (zh + 30 if zooms else 0)))
    # shelf packing
    rows, cur, cw = [], [], 0
    for bl in blocks:
        if cur and cw + bl[4] + gap > width - 2 * gap:
            rows.append(cur); cur, cw = [], 0
        cur.append(bl); cw += bl[4] + gap
    rows.append(cur)
    total_h = 150 + sum(max(b[5] for b in r) + gap for r in rows) + gap
    page = Image.new("RGB", (width, total_h), PAGE_BG)
    dr = ImageDraw.Draw(page)
    dr.text((gap, 30), title, fill=LABEL, font=font(48, True))
    dr.text((gap, 92), sub or ("Real use size: 1 px = 1 card px (300 ppi). Each cell: line on Limestone | reversed out of Spring Jade "
            "(geometric knockout). Framed insets below a cell: 3× zoom (line | knockout)."), fill=SUB, font=font(24))
    y = 150
    for r in rows:
        x = gap
        rh = max(b[5] for b in r)
        for spec, a, b, zooms, bw, _ in r:
            dr.text((x, y), f"{spec['title']}  {spec['ref']}", fill=LABEL, font=ft)
            dr.text((x, y + 34), spec["note"][:120], fill=SUB, font=fs)
            page.paste(a, (x, y + head))
            page.paste(b, (x + a.width + 12, y + head))
            if zooms:
                zy = y + head + max(a.height, b.height) + 18
                zx = x
                for z in zooms:
                    dr.rectangle([zx - 3, zy - 3, zx + z.width + 2, zy + z.height + 2], outline=(150, 150, 150), width=2)
                    page.paste(z, (zx, zy))
                    zx += z.width + 12
            x += bw + gap
        y += rh + gap
    return page


# ---------------------------------------------------------------------------
# back-scale integration test (knockout mode; NOT the back design)
# ---------------------------------------------------------------------------
def back_test():
    """Frame/lens/rosette motifs at the brief's back geometry (§H.19), all
    reversed out of the jade flood — to prove knockout mode at scale and to
    compare density with the Monarchs back. Darters, wild rice and comb
    sprays (Track B2) are absent, so coverage runs low by design."""
    cx, cy = T.CX, T.CY
    flood = G.rect_d(37.5, 37.5, 675, 975, 18)
    f = C.Frag()
    # outer rules (RULE at 49.5, FINE at 57.5), band inner rules (y 91.5 / x 79.5)
    rules = (C.stroke(G.rect_d(49.5, 49.5, 651, 951), T.RULE, style="rule")
             + C.stroke(G.rect_d(57.5, 57.5, 635, 935), style="rule")
             + C.stroke(G.rect_d(79.5, 91.5, 591, 867), style="rule"))
    # corner vent roundels; the rules break 4 px round them
    rnd = C.Frag()
    for x, y in ((68.5, 74.5), (681.5, 74.5), (68.5, 975.5), (681.5, 975.5)):
        rnd += M.vent_roundel(x, y, 56)
    f += C.cut(rules, C.region(rnd.outline()), 4.0) + rnd
    # top/bottom wave bands: springing from the band's inner rule, flowing outward
    top = M.running_wave_d2(cx, 91.5, 260, gap=36, rule=False) + M.fault_plinth(cx, 91.5, 60, hatch_step=0)
    top = C.cut(top, C.region(rnd.outline()), 4.0)
    f += top + top.mirror_y(cy)
    # side reed ladders with the medallion at y = 525
    # the band's own rules are the ladder rails (band 57.5–79.5 is 22 wide)
    lad = M.reed_ladder((68.5, 106), (68.5, 944), width=22, rails=False)
    med = M.reed_node_medallion(68.5, cy, 26, rot=90)
    lad = C.cut(lad, C.region(med.outline()), 4.2)
    f += lad + med + (lad + med).mirror_x(cx)
    # lens cartouche + offset field in the spandrels
    geo = M.lens_geometry(cx, 104, 946, 540)
    lens = M.lens_cartouche(geo)
    inner_frame = box(79.5 + 1.05 + 4.2, 91.5 + 1.05 + 4.2, 670.5 - 1.05 - 4.2, 958.5 - 1.05 - 4.2)
    field = M.lens_field(geo, count=7, clip_to=inner_frame.difference(C.region(lens.outline(grow=4.2))),
                         corners=[(79.5, 91.5), (670.5, 91.5), (79.5, 958.5), (670.5, 958.5)])
    f += lens + field
    # emblem: the rosette + C2 bubble triads
    f += M.source_rosette(cx, cy, 130)
    tri = C.bubble_triad(cx + 150, cy - 230, -60, (4.2, 6.3, 8.4))
    f += C.c2(tri)
    ko = C.knockout(flood, f)
    return flood, ko, f


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    which = set(argv) or {"geometric", "figurative"}
    OUT.mkdir(parents=True, exist_ok=True)
    CELLS.mkdir(parents=True, exist_ok=True)
    if "figurative" in which:
        from deck.motifs.sheet_figurative import main as fig_main
        fig_main()
    if "geometric" not in which:
        return
    specs = specimens()
    problems = []
    imgs = []
    for i, sp in enumerate(specs):
        for m in C.check(sp["frag"]):
            problems.append(f"{sp['title']}: {m}")
        for wmsg in sp["frag"].meta.get("warnings", []):
            problems.append(f"{sp['title']}: {wmsg}")
        imgs.append(build_cell(i, sp))
    page = compose(specs, imgs)
    page.save(OUT / "sheet-geometric.png", optimize=True)
    # back-scale knockout test
    flood, ko, _ = back_test()
    for ground, tag in ((T.PAPER, "limestone"), (T.WHITE, "white")):
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="750" height="1050" viewBox="0 0 750 1050">'
               f'<g id="paper"><path d="{G.rect_d(0, 0, 750, 1050, 37.5)}" fill="{ground}"/></g>'
               f'<g id="jade"><path d="{ko}" fill="{T.JADE}"/></g><g id="red"/><g id="gold"/><g id="ink"/></svg>')
        p = OUT / f"back-test-{tag}.svg"
        p.write_text(svg)
        render(p, OUT / f"back-test-{tag}-750.png", width=750)
        render(p, OUT / f"back-test-{tag}-188.png", width=188)
    rep = C.knockout_report(flood, ko, min_line=1.5, min_gap=3.0, res=0.25)
    (OUT / "report.txt").write_text(
        "deck.motifs specimen report\n"
        f"cells: {len(specs)}\n"
        f"back-test knockout coverage (paper lines / flood): {rep['coverage'] * 100:.1f}% "
        "(frame + lens + rosette only; darters, wild rice, comb sprays not yet placed)\n"
        f"paper slivers thinner than 1.5 px (opening test): {rep['thin_line_frac'] * 100:.2f}% of line area\n"
        f"jade gaps narrower than 3 px: {rep['thin_gap_frac'] * 100:.2f}% of flood area\n"
        + ("issues:\n" + "\n".join("  " + p for p in problems) if problems else "issues: none\n"))
    print((OUT / "report.txt").read_text())


if __name__ == "__main__":
    main()
