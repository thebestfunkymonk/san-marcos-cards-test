"""Specimen sheet for the FIGURATIVE motifs (Track B2, brief §G.2–6, 15, 24, 25).

    .venv/bin/python -m deck.motifs.sheet figurative     # from the project root

Writes
  build/motifs/sheet-figurative.png     every figurative motif at real size (1 px = 1 card
                                        px, 300 ppi): line on its ground | reversed out of
                                        Spring Jade (geometric knockout), with 3× zoom crops
  build/motifs/cells/f*.svg|png         the per-cell SVGs (layer groups paper/jade/red/gold/ink)
  build/motifs/fig-AS-*.png             the Ace of Spades lion in context (spade + lion + vent), 750 and
                                        188 px wide, on Limestone and on white
  build/motifs/fig-tuck-lens-*.png      the andante in its lens on Deep Hole board
  build/motifs/fig-seal-*.png           the blind salamander on the red seal disc
  build/motifs/report-figurative.txt    rule checks, stroke counts, tight spots, warnings
"""
from __future__ import annotations

import math
import subprocess
import sys
from pathlib import Path

import numpy as np
import shapely
from shapely.geometry import Point, Polygon

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from inkkit import geom as G  # noqa: E402

from deck import tokens as T  # noqa: E402
from deck.motifs import core as C  # noqa: E402
from deck.motifs import fauna as FA  # noqa: E402
from deck.motifs import forms as FM  # noqa: E402
from deck.motifs import geometric as M  # noqa: E402
from deck.motifs import hair as HR  # noqa: E402
from deck.motifs import lion as LI  # noqa: E402
from deck.motifs import rice as RI  # noqa: E402
from deck.motifs.sheet import CELLS, OUT, build_cell, compose, layered_svg, render  # noqa: E402


# ---------------------------------------------------------------------------
# context silhouettes
# ---------------------------------------------------------------------------
def spade_live() -> str | None:
    """Track A's Ace of Spades pip (read-only), if available."""
    try:
        from deck import frames as F
        return F.ace_pip_d("S")
    except Exception:
        return None


def spade_h13() -> str:
    """A spade rebuilt from the brief's §H.13 measurement table (u 340, top
    y 140: widest 340 at y 335, lobe lower edges ≈ 412, stem 40 → 68 px,
    plinth y 480–514) — used to show that the wing fit follows the silhouette."""
    cx = 375.0
    r = 78.0
    lc_y = 335.0
    lcx = 205.0 + r                      # lobe circles: widest point x 205 at y 335
    apex = np.array([cx, 140.0])
    circ_l = Point(lcx, lc_y).buffer(r, quad_segs=64)
    circ_r = Point(2 * cx - lcx, lc_y).buffer(r, quad_segs=64)
    # tangent from the apex to the right circle
    c = np.array([2 * cx - lcx, lc_y])
    d = np.hypot(*(c - apex))
    ang = math.atan2(c[1] - apex[1], c[0] - apex[0]) - math.asin(r / d)
    tan_len = math.sqrt(d * d - r * r)
    tr = apex + tan_len * np.array([math.cos(ang), math.sin(ang)])
    tl = np.array([2 * cx - tr[0], tr[1]])
    body = Polygon([apex, tr, (c[0], lc_y), (c[0] - 22, lc_y + 58), (cx, 402), (2 * cx - c[0] + 22, lc_y + 58),
                    (2 * cx - c[0], lc_y), tl]).buffer(0)
    body = shapely.union_all([body, circ_l, circ_r])
    stem = Polygon([(cx - 20, 395), (cx + 20, 395), (cx + 34, 480), (cx - 34, 480)])
    plinth = shapely.union_all([shapely.box(cx - 44.2, 480, cx + 44.2, 497), shapely.box(cx - 61.2, 497, cx + 61.2, 514)])
    sp = shapely.union_all([body, stem, plinth]).buffer(0)
    return G.from_shape(sp)


def lens_wreath_path(geo: dict, offset: float = 26.0, frac: float = 0.66, side: int = 1) -> np.ndarray:
    """One branch path for a wreath hugging a lens: from the bottom tip, up
    the (right, ``side`` = +1) arc offset ``offset`` px outward, for ``frac``
    of the side's height."""
    R = geo["R"]
    c = np.array(geo["c_left"] if side > 0 else geo["c_right"], float)   # the RIGHT arc is centred on the left
    top, bot = geo["top"], geo["bottom"]
    cx = geo["cx"]
    a_bot = math.degrees(math.atan2(bot - c[1], cx - c[0]))
    a_top = math.degrees(math.atan2(top - c[1], cx - c[0]))
    y_end = bot - frac * (bot - top)
    a_end = math.degrees(math.asin((y_end - c[1]) / R)) if side > 0 else 180 - math.degrees(math.asin((y_end - c[1]) / R))
    angs = np.linspace(a_bot, a_end, 240)
    pts = np.column_stack([c[0] + (R + offset) * np.cos(np.radians(angs)), c[1] + (R + offset) * np.sin(np.radians(angs))])
    # lead in from the knot below the tip
    knot = np.array([cx, bot + offset * 0.9])
    return np.vstack([knot, pts])


def tuck_lens_demo() -> C.Frag:
    geo = M.lens_geometry(0, -220, 220, 330)
    lion = LI.lion_andante(0, 0)
    rule = C.stroke(geo["d"], color=T.FOIL)
    path = lens_wreath_path(geo, 26.0, 0.66)
    wreath = RI.rice_wreath(path, axis=0.0, pitch=58.0, first=40.0, leaf_len=110.0, ratio=12.0,
                            angle=22.0, color=T.FOIL)
    # the wreath lies over the lens rule: the rule breaks 4.2 px round the leaves (interlace, §B.2)
    rule = C.cut(rule, wreath.shape(), 4.2)
    return lion + rule + wreath


# ---------------------------------------------------------------------------
# specimens
# ---------------------------------------------------------------------------
def specimens():
    S = []

    def add(title, ref, note, f, zoom=None, ground=T.PAPER, under=(), view=None):
        S.append(dict(title=title, ref=ref, note=note, frag=f, zoom=zoom, ground=ground, under=list(under),
                      view=view))

    sp = spade_live()
    if sp:
        lion = LI.lion_moleca(375, 262, silhouette=sp)
        add("Lion in moleca — fitted to the Ace of Spades (Track A pip)", "§G.2 / H.13",
            "face Ø60, mane r36/48/60, wings fitted 12 px inside the spade, curls toward the apex; paws on the vent",
            lion, zoom=(318, 150, 432, 262), under=[(sp, T.INK)], view=G.bbox(sp))
    sp13 = spade_h13()
    lion13 = LI.lion_moleca(375, 262, silhouette=sp13)
    add("Lion in moleca — refitted to a §H.13-table spade", "§G.2 fit",
        "same call, other silhouette: the wing guide, fan lengths and curl stop are all computed from it",
        lion13, zoom=(440, 250, 560, 430), under=[(sp13, T.INK)], view=G.bbox(sp13))
    marks = C.Frag()
    for i, s_ in enumerate((60, 48, 40, 32, 24)):
        marks += LI.lion_mark(40 + i * 72, 40, s_)
    add("Lion Mark — line", "§G.2 simplified", "60 · 48 · 40 · 32 · 24 px wide; ≤ 24 strokes; detail tiers full / badge / tiny",
        marks, zoom=(0, 12, 120, 70))
    clasps = C.Frag()
    for i, s_ in enumerate((60, 48, 40, 32, 24)):
        clasps += LI.lion_mark(40 + i * 72, 40, s_, style="solid")
    add("Lion Mark — solid clasp on Gill Red", "§G.2 / §C rule 4",
        "flat gold silhouette + Aquifer contour and details (gold on red only as a contoured solid)",
        clasps, zoom=(0, 12, 120, 70), under=[(G.rect_d(-20, -10, 420, 100), T.RED)])
    geo = M.lens_geometry(0, -220, 220, 330)
    andante = LI.lion_andante(0, 0)
    lens_rule = C.stroke(geo["d"], color=T.FOIL)
    add("Lion andante in the 330 × 440 lens (gold on Deep Hole)", "§G.3 / H.20",
        "walks left; forepaws on a 3-course half-hatched ledge, hind paws in 3 ripples; tail tuft + Ø6.3 terminal",
        andante + lens_rule, zoom=(-160, -120, -10, 30), ground=T.BOARD)
    leaves = (RI.ribbon_leaf(0, 60, -14, 170, bend=(12, -12)) + RI.ribbon_leaf(0, 110, -8, 190, bend=(9, 9), hatch=-1)
              + RI.ribbon_leaf(0, 150, 0, 150, bend=(0, 0)))
    add("Wild-rice ribbon leaves", "§G.4", "S midrib of two tangent arcs; vesica profile 10–14 : 1; one half hatched perpendicular to the midrib",
        leaves, zoom=(40, 20, 150, 80))
    stalks = RI.rice_stalk(0, 200, -90, 190) + RI.rice_stalk(80, 200, -80, 180, bend=-12)
    add("Wild-rice flowering stalk", "§G.5", "erect female spikelets (3:1, 6 px pedicels, ±15°, HAIRLINE awns) above; drooping male florets (±150°) below",
        stalks, zoom=(-30, 0, 50, 90))
    wreath = RI.rice_wreath_arc(0, 0, 150)
    add("Wild-rice wreath (Ace of Clubs half-arc, 4 to 8 o'clock)", "§G.6 / H.15",
        "paired streaming ribbon leaves every 14°, −6 % per pair; flowering spikes at the tips; reed-node knot",
        wreath, zoom=(-60, 110, 60, 175))
    plumes = C.Frag()
    for i in range(3):
        plumes += FA.gill_plume(f"M{i*48} 110 C {i*48+6} 70 {i*48+24} 40 {i*48+40} 20", n=7 - (i == 2))
    add("Gill plumes (Gill Red)", "§G.15", "curved spine, 6–8 barbs on one side shortening to the tip, Ø4.2 tip dot",
        plumes, zoom=(-5, 15, 60, 80))
    cur = (HR.current_lines("M0 0 C 20 40 20 80 60 110", 3) + HR.current_lines("M60 0 C 80 40 80 80 120 110", 4)
           + HR.current_lines("M130 0 C 150 40 150 80 190 110", 5, gold="alternate")
           + HR.current_lines("M200 0 C 220 40 220 80 260 110", 4, gold="lock"))
    add("Current lines (hair, beards, plumes)", "§G.24", "3 · 4 · 5 lines at 7 px from one guide, staggered Ø6.3 terminals; alternate / whole lock in flat gold",
        cur, zoom=(120, 50, 230, 120))
    # the tuck front's lens: lion andante + a wreath following the lens contour (§H.20 items 4–5)
    tuck = tuck_lens_demo()
    add("Tuck lens: andante + wild-rice wreath on the lens contour", "§H.20 items 4–5",
        "rice_wreath(path) follows any path: here the lens outline offset 26 px, lower two-thirds, knot at the foot",
        tuck, zoom=(60, 60, 200, 230), ground=T.BOARD)
    darters = (FA.fountain_darter(60, 20, 100) + FA.fountain_darter(60, 70, 100, facing=-1)
               + FA.fountain_darter(250, 45, 150))
    add("Fountain darter", "§G.25", "6:1; fanned 9-spine first dorsal with membrane scallops; stitch line 7/4; saddle bars; eye with dot; ±facing",
        darters, zoom=(170, 15, 330, 75))
    seal_d = G.circle_d(0, 0, 165)
    sal = FA.blind_salamander(0, 0)
    add("Texas blind salamander (seal, gold on Gill Red)", "§H.20 seal",
        "curled in a single C; spatulate snout; vestigial dot eyes; 3 feathery gills a side; long thin limbs; costal grooves; finned tail",
        sal, zoom=(10, -100, 110, 0), under=[(seal_d, T.RED)], view=(-165, -165, 165, 165))
    return S


# ---------------------------------------------------------------------------
# context renders (Ace of Spades, tuck lens, seal) at 750 / 188 on Limestone and white
# ---------------------------------------------------------------------------
def _ctx(name, f, view, under, grounds=((T.PAPER, "limestone"), (T.WHITE, "white")), widths=(750, 188)):
    outs = []
    for ground, tag in grounds:
        svg = layered_svg(f, view, ground=ground, under=under)
        p = OUT / f"{name}-{tag}.svg"
        p.write_text(svg)
        for wpx in widths:
            png = OUT / f"{name}-{tag}-{wpx}.png"
            render(p, png, width=wpx)
            outs.append(png)
    return outs


def context_renders():
    outs = []
    sp = spade_live()
    card = (0, 0, 750, 1050)
    if sp:
        lion = LI.lion_moleca(375, 262, silhouette=sp)
        # a minimal Ace of Spades context: the spade, the lion; the conduit/legend are the Ace of Spades artist's
        outs += _ctx("fig-AS", lion, card, [(sp, T.INK)])
    tuck = tuck_lens_demo().translate(384.5, 540.0)          # the tuck front's lens at y 320–760
    outs += _ctx("fig-tuck-lens", tuck, (0, 0, 769, 1069), [(G.rect_d(0, 0, 769, 1069), T.BOARD)],
                 grounds=((T.BOARD, "board"),), widths=(769, 192))
    sal = FA.blind_salamander(165, 165)
    outs += _ctx("fig-seal", sal, (0, 0, 330, 330), [(G.circle_d(165, 165, 165), T.RED)],
                 grounds=((T.PAPER, "limestone"),), widths=(330, 83))
    return outs


# ---------------------------------------------------------------------------
# report
# ---------------------------------------------------------------------------
def report(specs) -> str:
    lines = ["deck.motifs figurative specimen report", ""]
    for sp in specs:
        f = sp["frag"]
        issues = C.check(f)
        warns = f.meta.get("warnings", [])
        ts = FM.tight_spots(f, 4.2)
        lines.append(f"{sp['title']} [{sp['ref']}]: marks {len(f.marks)}, rule issues {len(issues)}, "
                     f"ground narrower than 4.2 px: {ts['area']:.0f} px²")
        for m in issues[:5]:
            lines.append(f"   ! {m}")
        for m in dict.fromkeys(warns):
            lines.append(f"   ~ {m}")
    for s_ in (60, 48, 40, 32, 24):
        m = LI.lion_mark(0, 0, s_)
        lines.append(f"Lion Mark {s_} px: {m.meta['strokes']} strokes ({m.meta['detail']}), "
                     f"width {m.bbox()[2] - m.bbox()[0]:.1f} px")
    return "\n".join(lines) + "\n"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    CELLS.mkdir(parents=True, exist_ok=True)
    specs = specimens()
    imgs = [build_cell(i, sp, prefix="f") for i, sp in enumerate(specs)]
    page = compose(specs, imgs, title="HEADWATERS · ornament library · figurative motifs (§G.2–6, 15, 24, 25)",
                   sub="Real use size: 1 px = 1 card px (300 ppi). Each cell: line on its ground (paper, or the Ace of Spades "
                       "spade / tuck board / red seal shown as a preview underlay) | reversed out of Spring Jade "
                       "(geometric knockout). Framed insets: 3× zoom.")
    page.save(OUT / "sheet-figurative.png", optimize=True)
    context_renders()
    rep = report(specs)
    (OUT / "report-figurative.txt").write_text(rep)
    print(rep)


if __name__ == "__main__":
    main()
