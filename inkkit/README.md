# inkkit

Pure-Python toolkit for premium vector line art on playing cards: monoline
Americana (Monarchs/Drifters) and engraved styles, filigree, guilloché,
borders, botanicals, suits and heraldry, outlined type, print separations with
real knockouts, and preflight checks. Everything is SVG path data at
750×1050 px (2.5×3.5 in @ 300 ppi). Built on numpy, shapely 2, skia-pathops,
scipy and fontTools; renders with `rsvg-convert`.

```
inkkit/
  svg.py        string SVG builder, layered Doc, separations (knockouts, traps), fit_paths
  geom.py       path data <-> polylines/shapely/pathops, booleans, offsets, transforms, Curve,
                knockout, interlace, fillet_junction, round_corners, fit_curves (Béziers)
  stroke.py     variable-width tapered / calligraphic strokes; line styles (taper/monoline/outline/inline)
  hatch.py      parallel/cross/half/contour/flow/along hatching, tonal engraving, tones, stipple, dot screens
  ornament/     scrollwork (volutes, filigree), guilloche, borders (frame_strip, ribbon), botanical,
                radiance (fleurons), patterns
  suits.py      pips (brief §E.1 geometry or classic), pip layouts, corner indices, court frame, ace keyline
  heraldry.py   Petra Sancta tinctures, shields, crowns
  typeset.py    text -> outlined paths (variable fonts, GPOS kerning, text on path); alias: type.py
  card.py       card constants, two-headed composition, render, contact sheets, safe zone
  preflight.py  thin-line / plugging-gap report and overlay per printed plate
  tokens.py     palette + line weights (creative brief) and print profiles
  demo.py       renders demo/*.svg|png, one sheet per module + showpiece (+ plates, preflight)
  examples/     complete pieces built only from the public API
  tests/        test_smoke.py (plain asserts; run as a script)
```

Run from the project root:

```sh
.venv/bin/python inkkit/demo.py              # all sheets (≈1 min) -> inkkit/demo/
.venv/bin/python inkkit/demo.py showpiece    # one sheet
.venv/bin/python inkkit/tests/test_smoke.py  # 27 tests (≈1 min); add a name filter: ... test_smoke.py geom
```

## Quick start

```python
import sys; sys.path.insert(0, ".")          # project root
import numpy as np
from inkkit import svg, geom as G, stroke as S, hatch as H, card, tokens as T
from inkkit import ornament as O, suits as SU, heraldry as HR, preflight as PF
from inkkit.typeset import text_to_path

doc = card.new_card(T.PAPER)                               # rounded card on the 'paper' layer
doc.add_def(svg.foil_gradient("foil", T.FOIL))             # preview-only metallic fill
doc.layer_style("foil", fill="url(#foil)")                 # everything on 'foil' inherits it
doc.add(svg.path(O.frame(24, 24, 702, 1002, r=18)), layer="ink")
doc.add(svg.path(O.filigree_corners((50, 50, 650, 950), 150, 3, style="monoline", lw=T.FINE)), layer="foil")
doc.add(svg.path(SU.pip("spade", 375, 525, 200, style="half")), layer="ink")
d, bbox, adv = text_to_path("Cinzel", "SAN MARCOS", 44, 375, 250, anchor="middle",
                            variations={"wght": 700}, tracking=160)
doc.add(svg.path(d, fill=T.INK), layer="ink")
doc.save("/tmp/quick.svg")
card.render("/tmp/quick.svg", "/tmp/quick.png", 1500)
doc.save_layers("/tmp/quick-sep")          # one plate per layer: ink = black, knockouts = white
print(PF.summary(PF.preflight(doc)))       # thin lines / plugging gaps per plate
```

## Conventions

* **Units** are SVG px, y down; the card is `0 0 750 1050`, corner radius 37.5.
  Angles are screen degrees (0 = +x, 90 = down, −90 = up); `cw=True` curls
  clockwise *on screen*.
* **Everything returns SVG path data (`d` strings).** Inputs that say
  *pathlike* accept a d-string, an (N,2) array/list of points, a list of
  those, `(points, closed)` tuples, a `geom.Curve`, or shapely geometry.
* **Winding**: every FILL output is wound **clockwise on screen** (holes
  counter-clockwise), including circles, ellipses, text, mirrored copies
  (`mirror_*`/`transform` re-wind closed subpaths under reflection) and
  shapely round trips. FILL pieces therefore compose by plain string
  concatenation under the default nonzero rule; use `geom.union` when you
  need one clean, non-overlapping outline, and `geom.orient(d, "cw")` for
  hand-built pieces.
* **FILL vs STROKE**: every docstring ends in `-> FILL d` (draw with `fill=`)
  or `-> STROKE d` (centrelines; draw with `fill="none" stroke=… stroke-width=…`).
  Line-art generators take `width=` (hatch/guilloche) or `lw=`
  (borders/botanical): **None → STROKE, a number → FILL outlines**.
  Generators whose output would then mix STROKE lines with solid parts
  (band triangles/dots, fan hub, sprig berries …) require `parts=True` and
  return `{'stroke': d, 'fill': d}`; FILL-only generators (patterns,
  starburst, sunburst lines, egg-and-dart, corner_rosette 'flower'/'star')
  raise a clear `ValueError` for `lw=None`.
* **Empty input** (e.g. a shape consumed by `inset=` or an empty
  `difference()`) returns `''`; invalid enum strings and degenerate numbers
  raise `ValueError` with the allowed values.
* **Numbers** are written on a 0.01 px grid with drift-free relative commands.
  Nothing emits `<text>`, `<image>`, external refs or filters.
  `Doc.save(path, fit=0.05)` refits paths with cubic Béziers (1.2–3.5×
  smaller, editable in Illustrator; deviation ≤ `fit` px).
* **Determinism**: all randomness is seeded (`seed=`), so re-runs are byte-identical.
* **Layers and separations**: `Doc(layers=(...))`, `doc.add(..., layer=, knockout=False)`.
  `doc.separations()` / `doc.save_layers(prefix)` write one plate per printed
  layer: that layer's ink colours → black; paper/white fills and
  `knockout=True` content → white (knocked out); every layer *above* it is
  painted white on top (knocks out), except layers in `overprint=`;
  `trap=` px chokes those knockouts; masks/clip paths/defs are untouched,
  `<use>` is expanded, opacity is flattened with a warning, and a plate that
  mixes several ink colours warns. `geom.knockout()` cuts the same knockouts
  into the geometry itself.

### Line weights and print minimums (750×1050 @ 300 ppi; 1 px ≈ 0.085 mm)

| use | px | token |
|---|---|---|
| absolute minimum, offset litho positive line (0.25 pt) | 1.05 | `PRINT_PROFILES['ink_offset']['min_line']`, `MIN_LINE` |
| reversed (knocked-out) line in a solid | 1.8 | `MIN_REVERSED` |
| gap between strokes that must not plug | 1.2 | `MIN_GAP` |
| foil / metallic minimum line (brief HAIRLINE), gap 2.4 | 1.6 | `PRINT_PROFILES['foil']`, `HAIRLINE` |
| conservative hot-foil (0.2 mm line / 0.25 mm gap) | 2.4 / 3.0 | `PRINT_PROFILES['foil_strict']` |
| the monoline: ornament, hatching (brief) | 2.1 | `FINE` |
| interior detail / knockout lines in pips | 3.1 | `MEDIUM` |
| frames and rules | 4.2 | `RULE` |
| figure silhouettes | 6.25 | `CONTOUR` |

Guilloché at card scale: 1.05–1.2 px lines with ≥ 1.5 px between them
(`auto_lines=True` enforces it). Hatch: FINE lines at a 7 px pitch
(`HATCH_PITCH`), butt ends meeting the contour's centreline. Engraving:
`wmax ≈ 0.6–0.7 × spacing`; `engrave(gap=0.9, min_width=1.05)` are the
defaults so no sliver prints. Tapered ornaments take `min_width` (default the
offset minimum; pass `PRINT_PROFILES['foil']['min_line']` and `gap=2.4` for
foil). Check any piece with `preflight`.

## API reference

The snippets below assume the Quick-start imports and run as-is.

### svg — builder, layered document, separations

```python
svg.fmt(1.2349)                                    # '1.23'
svg.attrs(stroke_width=2, class_="a", sw=1)        # ' stroke-width="1" class="a"' — last duplicate wins
svg.el("desc", "a < b & c")                        # text children are escaped
p = svg.path("M0 0L10 10", stroke=T.INK, stroke_width=1.5, fill="none")
grp = svg.g(p, svg.circle(5, 5, 2), transform=svg.tf(svg.translate(10, 0), svg.rotate(45, 5, 5)))
shapes = [svg.ellipse(0, 0, 4, 2), svg.rect(0, 0, 8, 8, rx=2), svg.line(0, 0, 5, 5, stroke="#000"),
          svg.polyline([(0, 0), (5, 5)]), svg.polygon([(0, 0), (5, 0), (2, 4)]), svg.use("sym", 3, 3),
          svg.clip_path("c1", svg.circle(0, 0, 5)), svg.mask("m1", svg.rect(0, 0, 5, 5, fill="#fff")),
          svg.linear_gradient("lg", [(0, "#000"), (1, "#fff", 0.5)], 0, 0, 1, 1),
          svg.radial_gradient("rg", [(0, "#fff"), (1, "#000")]), svg.defs(svg.rect(0, 0, 1, 1)),
          svg.symbol("sym", svg.circle(0, 0, 1), viewBox=(-1, -1, 2, 2)), svg.foil_gradient("fg", "gold"),
          svg.scale(2), svg.matrix(1, 0, 0, 1, 5, 5)]
svg.parse_color("#b95"), svg.parse_color("rgb(20,40,60)"), svg.to_hex("white")
doc = svg.Doc(750, 1050, bg=T.PAPER)              # layers paper/ink/red/foil (+ any you add)
doc.uid("clip")                                    # 'clip1' — unique ids
doc.add_def(svg.foil_gradient("foil"))
doc.layer_style("foil", fill="url(#foil)")         # attributes on the layer <g>
doc.add(p, grp, layer="ink")
doc.add(svg.path(G.circle_d(100, 100, 20), fill=T.PAPER), layer="ink")   # paper fill = knockout
doc.add(svg.path(G.circle_d(200, 100, 20)), layer="ink", knockout=True)  # explicit knockout
xml = doc.to_string()                              # or doc.save(path, fit=0.05) / doc.render(png, width)
plates = doc.separations(trap=1.2, overprint=("foil",))   # {layer: svg}
files = doc.save_layers("/tmp/sep")                # one plate per printed layer
small = svg.fit_paths(xml, 0.05)                   # Bézier-refit any SVG string
```

### geom — paths, booleans, knockouts, interlace, curves

```python
d = "M10 10 C 40 -10 80 30 110 10 A 20 20 0 0 1 110 50 Z"
cmds = G.parse_d(d)                  # absolute M/L/C/Q/Z tuples (H/V/S/T/A expanded); bad data raises
d2 = G.cmds_to_d(cmds)               # compact relative d
polys = G.flatten(d, tol=0.05)       # [(points, closed)]
G.as_polys([[0, 0], [5, 5]])         # normalise any pathlike
G.poly_d([[0, 0], [10, 0], [10, 10]], closed=True, orient="cw"); G.polys_d(polys); G.join_d(d, [[0, 0], [1, 1]])
G.signed_area([[0, 0], [10, 0], [10, 10]])                                # > 0: clockwise on screen
shape = G.to_shape(d, "nonzero"); G.from_shape(shape.buffer(2))          # shapely bridge (oriented)
sk = G.to_skia(d); G.from_skia(sk)                                        # skia-pathops bridge
a, b = G.circle_d(0, 0, 20), G.rect_d(0, -20, 40, 40, 6)
G.union(a, b); G.difference(a, b); G.intersection(a, b); G.xor(a, b)     # exact, curves kept
G.resolve(a + G.circle_d(0, 0, 10), "evenodd")                            # remove overlaps
G.orient(G.reverse(b), "cw")                                              # force winding of closed subpaths
G.clip([[-50, 0], [50, 0]], b); G.clip_out([[-50, 0], [50, 0]], b)        # STROKE art inside / outside
G.offset(b, 4, join="miter"); G.offset(b, -3)                             # grow / inset
G.outline("M0 0 L100 0", 3, cap="round")                                  # stroke -> FILL
G.fillet(G.star_d(0, 0, 40, 18, 5), 4)                                    # round every corner (closed)
G.round_corners("M0 0 L50 0 L50 50", 8)                                   # tangent arcs (open or closed)
G.knockout(H.parallel(b, 45, 7, width=2.1), a, gap=2)                     # FILL art minus occluder+gap
G.knockout(H.parallel(b, 45, 7), a, gap=2, lines=True, lw=2.1)            # STROKE lines stop short
G.interlace(["M0 0 L100 100", "M0 100 L100 0"], width=2.1, gap=4.2)       # over/under, alternating
G.fillet_junction(G.union(S.stroke("M0 50L50 0", 6), S.stroke("M50 0L100 50", 6)), (50, 0), 4)
G.fit_curves(G.poly_d(G.arc_pts(0, 0, 50, 0, 300)), tol=0.05)            # polyline -> cubic Béziers
G.simplify(d, 0.2); G.bbox(d); G.area(b)
G.translate(d, 5, 0); G.rotate(d, 30, 375, 525); G.scale(d, 2, cx=375, cy=525)
G.transform(d, (1, 0, 0.3, 1, 0, 0))                                      # SVG matrix (a,b,c,d,e,f)
G.rotate([(0, 0), (10, 0)], 90)                                           # point lists stay (N,2) arrays
G.mirror_x(d, 375); G.mirror_y(d, 525); G.mirror_line(d, (0, 0), 45)       # reflections keep CW winding
G.bilateral(d, 375)                   # d + its mirror — bilateral symmetry
G.rotate180(d)                        # about the card centre (two-headed courts)
G.repeat_rotational(G.star_d(375, 400, 10, 4, 5), 8, 375, 525)
G.reverse(d)
cv = G.Curve("M0 0 C 50 -40 100 40 150 0")      # arc-length parametrised
cv.length, cv.at(0.5), cv.tangent(0.5), cv.normal(0.5), cv.angle(0.5)
cv.resample(4); cv.sample(20); cv.sub(0.2, 0.8); cv.offset(3); cv.reversed(); cv.d()
G.Curve(G.circle_d(0, 0, 10)).sub(0.9, 0.1)     # closed curves wrap across the seam
cv.map(np.array([[10.0, 5.0]]))                 # strip coords (arc-length u, normal v) -> page
G.curve(d); G.resample(d, 5, keep_corners=30); G.point_at(d, .5); G.tangent_at(d, .5); G.normal_at(d, .5)
G.smooth_d([(0, 0), (40, -30), (80, 10)]); G.spline([(0, 0), (40, -30), (80, 10)])
G.circle_d(0, 0, 5); G.ellipse_d(0, 0, 8, 4, 30); G.rect_d(0, 0, 10, 10, 2)
G.arc_pts(0, 0, 10, 0, 90); G.polygon_d(0, 0, 10, 6); G.star_d(0, 0, 10, 4, 5)
```

### stroke — tapered / swelled / calligraphic strokes and line styles (→ FILL)

```python
path = "M60 500 C 200 380 380 640 520 500"
S.stroke(path, 8)                                   # uniform, round caps (exact buffer; any width is fast)
S.stroke(path, 8, "taper-both", taper=0.35, min_width=1.05)   # tapers end in a printable round cap
S.stroke(path, 8, "taper-end")                      # also: taper-start, swell, teardrop, teardrop-rev,
S.stroke(path, 8, "scroll", end_ratio=0.15, terminal="ball", terminal_r=4)  # hairline-end, nib, uniform
S.stroke(path, 8, "taper-both", taper=0.2, power=0.3)          # blunt tips, no fishtails
S.stroke(path, 10, "nib", nib_angle=40, nib_min=0.15)          # broad-nib contrast
S.stroke(path, lambda t: 2 + 6 * t)                 # width as a function of arc-length fraction t
S.stroke(path, 6, cap="pointed")                    # short automatic taper at the ends
S.stroke(G.circle_d(375, 525, 60), 6, "nib", nib_angle=0)      # closed paths too
S.stroke_many([path, G.translate(path, 0, 30)], width=4)
S.variable_stroke(np.array([[0, 0], [50, 0], [100, 0.0]]), np.array([0.5, 4, 0.5]))  # low level
S.styled(path, 10, "swell", style="monoline", lw=2.1)          # STYLES: taper | monoline | outline | inline
f = S.profile_fn("swell"); S.ease(0.5); S.PROFILES; S.STYLES
```

Robustness: the outline is the exact envelope of a disc sweep. Wherever the
inner offset would fold (tight spirals, hairpins, sharp corners) or the width
changes faster than the arc length (steep tapers), that stretch is rebuilt
from disc hulls and unioned with skia-pathops, so strokes match the exact
union of discs to <1% (see `tests/test_smoke.py::test_stroke_fold_safety_and_tips`).

### hatch — engraving fills (STROKE, or FILL with `width=`)

```python
shield = "M40 40H210V140C210 185 170 215 125 235C80 215 40 185 40 140Z"
H.parallel(shield, 30, 4)                                # STROKE lines clipped exactly
H.parallel(shield, 30, 4, width=1.1, taper=8, min_width=1.05)   # FILL, lines fade to round caps
H.parallel(shield, 45, 7, width=2.1, cap="butt")         # brief hatch: butt ends on the contour
H.cross(shield, (45, -45), 5, width=1.05)
H.half(shield, [(125, 30), (125, 250)], side=1, angle=45, spacing=7)   # Monarchs half-hatch
H.contour(shield, 5)                                     # offset / contour hatching
H.concentric(shield, (125, 140), 5); H.radial(shield, (125, 140), 72, r0=10)
H.flow(shield, lambda x, y: np.arctan2(y - 140, x - 125) + np.pi / 2, 5, width=1.1,
       singular=[(125, 140)])                            # streamlines; ends that meet a neighbour taper
H.along(shield, "M0 160 C 80 80 160 220 260 140", 5)    # wave hatch following a guide
H.between("M40 60 C 120 40 160 80 210 60", "M40 200 C 120 240 160 180 210 210", 12, clip=shield)
tone = H.sphere_tone(125, 140, 80)                       # 0 highlight .. 1 shadow
H.cylinder_tone((125, 40), (125, 235), 85); H.bevel_tone(shield, -135, 12)
H.shape_distance_tone(shield, 10); H.linear_tone((0, 0), (200, 0)); H.radial_tone((125, 140), 80)
H.clamp_tone(tone)
lines = H.latitudes(125, 140, 80, 4, tilt_deg=-15, rot_deg=-25)
H.engrave(lines, tone, wmin=0.6, wmax=2.6, clip=G.circle_d(125, 140, 80), fade=4, edge_gap=1.5)
H.tonal(shield, tone, angle=-30, spacing=4, cross_at=0.6, fade=5, edge_gap=1.5)   # + cross in deep shadow
H.stipple(G.circle_d(125, 140, 80), tone, dmin=2.4, dmax=10)               # Poisson-disk stipple
H.dot_screen(shield, 7, 1.6, tone=tone, r_min=0.6, fade=8)                 # regular dot field / halftone
H.emit(H.lines_of("M0 0L10 0"), width=2.1, taper=3)                        # lines -> FILL
```

`engrave` breaks each line where it falls below `gap` (staggered per line by
`stagger` so highlight edges dissolve), tapers each piece over `taper_len`
(default 3·wmax) down to `min_width`, keeps `edge_gap` px of paper inside the
clip and eases widths toward it over `fade` px.

### ornament — scrollwork

```python
O.scroll((40, 120), 0, 180, 1.4, width=7, leaves=3)         # Ionic volute (law='log') with acanthus
O.scroll((40, 120), 0, 180, 1.4, width=7, terminal="eye")   # disc in the volute eye
O.scroll((40, 120), 0, 180, 1.4, style="monoline", lw=2.1)  # styles: taper|monoline|outline|inline
d, centre = O.scroll((40, 120), 0, 180, centerline=True)    # attach things to the centreline
O.s_scroll((60, 330), (300, 250), width=6); O.c_scroll((420, 320), (690, 320), width=6)
O.volute((0, 0), 0, 120, 1.5, tighten=2.2)                  # log-spiral centreline, even turn spacing
O.volute_eye(O.volute((0, 0), 0, 120, 1.5))                 # (centre, radius) of the eye
O.curl((0, 0), 0, 120, turns=1.2, power=2.0)                # clothoid-family centreline (points)
O.log_spiral((0, 0), 60, 4, 2); O.s_curve(200, (1, 1), "S"); O.fit(O.s_curve(200), (0, 0), (100, 0))
fl = O.flourish(np.array([[0, 0], [60, -30], [120, 0]]), end_turns=1.2, end_size=30)   # G2 volute ends
O.branch(fl, 0.4, side=1, length=40, turns=1.0)             # tangent offshoot (fillet its crotch)
S.stroke(fl, 5, "scroll", terminal="ball", min_width=1.05)
O.acanthus_leaf((0, 0), -60, 40, 14, lobes=3); O.acanthus_leaf((0, 0), -60, 40, 14, style="outline")
O.filigree_corner(160, 3, x=60, y=60, corner="tl")          # complexity 1..3; tl/tr/bl/br
O.filigree_corner(160, 3, style="outline", lw=1.2, min_width=1.6, gap=2.4)   # foil-safe open-face
O.filigree_corners((60, 60, 630, 930), 160, 2)
O.filigree_band(500, 40, x=375, y=300, center="bud")        # symmetric rinceau band
O.place_corner(G.rect_d(0, 0, 10, 10), 700, 40, "tr")
```

Volutes are built to an explicit law: `law='log'` shrinks each turn by
`tighten`, `auto_turns` drops turns until successive turns keep the print
gap, and ball/eye terminals are sized to clear the previous turn.

### ornament — guilloché (STROKE; draw at ≥ 1.05 px)

```python
O.spirograph(375, 525, 80, 30, 42)                          # hypotrochoid; kind="epi" for epitrochoid
O.spiro_rosette(375, 525, 75, 30, 30, copies=5)             # copies evenly within the petal period
R, r, dd = O.spirograph_fit(60, 90, petals=12, loops=5)      # choose R, r, d by radius
O.spirograph(375, 525, R, r, dd)
O.rosette(375, 525, 80, 130, lobes=24, lines=12, phase_span=0.5, shape=0.85, auto_lines=True)
O.rosette_ring(375, 525, 20, 130, bands=3, lobes=(12, 24, 36), lines=8)
O.guilloche_band(G.circle_d(375, 525, 150), 14, wavelength=14, lines=8, amps=(1, 0.55))
O.guilloche_band(G.rect_d(40, 40, 200, 200), 14)            # sharp corners are rounded first
O.guilloche_frame(36, 36, 678, 978, 14, width=13, lines=7)
O.guilloche_strip((100, 100), (650, 100), 12)
O.wave_lattice(G.rect_d(100, 100, 300, 200), 7, 3, 28)      # banknote lens mesh
O.min_line_gap(O.rosette(0, 0, 40, 80, lines=10))           # closest parallel run (fusing check)
O.wave(np.linspace(0, 6, 5), 0.7)
```

### ornament — borders & frames

```python
O.frame(22, 22, 706, 1006, r=20, corner="round", style="classic")   # corner: round|square|notch|
O.rules(40, 40, 670, 970, [(0, 2.5), (6, 1.2)], r=12, corner="notch")  #       chamfer|step|step2
O.frame_shape(40, 40, 670, 970, 20, "step2", inset=10)             # closed outline (clip/fill)
fp = O.frame_path(40, 40, 670, 970, 24, "round", inset=12)         # centreline for strip motifs
O.frame_strip(40, 40, 670, 970, "band", 14, fill="triangles")      # per side + corner blocks
O.frame_strip(40, 40, 670, 970, "egg_and_dart", 20, corner="rosette")
O.frame_strip(40, 40, 670, 970, "rope", 12, corner=lambda x, y, s: G.circle_d(x, y, s / 3))
O.corner_block(60, 60, 12, style="diamond")
O.beaded(fp, 2, 2.4, alternate=1.2)
O.rope(fp, 9, 6); O.rope(fp, 9, 6, style="line", lw=1.05); O.dentil(fp, 6, 4, 3)
O.band(fp, 12, "triangles", lw=1.05)       # zigzag|triangles|ladder|diamond|chevron|dots|none
O.band(fp, 12, "dots", lw=None, parts=True)                        # {'stroke', 'fill'}
O.greek_key((60, 60), (690, 60), 14); O.greek_key_frame(40, 40, 670, 970, 14)
O.egg_and_dart("M60 900 L690 900", 20)
O.corner_rosette(60, 60, 20, style="flower")                       # flower|daisy|star
O.cartouche(375, 900, 220, 60, "ogee")                             # tab|oval|ogee|bracket|shield
rb = O.ribbon(200, 550, 820, 26, sag=10)                           # front/tails/back/silhouette/lines/path
O.ribbon(200, 550, 820, 26, ends="roll")                           # rolled scroll ends
O.fit_repeats(100, 7)
```

`ribbon()` draws only what is visible (tails and fold never overlap the
front); hatch `rb["back"]`, and use `rb["silhouette"]` as a knockout for
whatever lies behind it.

### ornament — botanical

```python
O.leaf((0, 0), (40, -60), 22, style="outline", hatch="half")       # Monarchs half-hatched leaf
O.leaf((0, 0), (40, -60), 22, style="solid"); O.leaf((0, 0), (40, -60), 22, style="engraved")
O.leaf((0, 0), (40, -60), 22, style="outline", hatch="veins")      # curved side veins
outline, midrib, left_half, right_half = O.leaf_shape((0, 0), (40, -60), 22, "ovate")
O.sprig("M0 0 C 40 -30 80 -80 100 -130", count=7, style="outline", hatch="half", jitter=0.5, seed=2)
O.sprig("M0 0 L0 -130", style="outline", lw=None, berries=3, parts=True)   # STROKE + FILL parts
O.laurel("M0 0 C 40 -30 80 -80 100 -130", berries=3)
O.wreath(375, 525, 180, gap_deg=70, jitter=0.4)
O.grass((375, 900), count=11, height=150)
O.rice("M300 900 C 300 800 330 740 400 720", leaves=4, current=35)  # Texas wild rice + streaming leaves
O.flower(375, 525, 30, shape="heart"); O.palmate_leaf((375, 900), -150, 50, style="outline")
bb = O.bluebonnet((375, 900), 200, parts=True)                     # {'stem','flowers','tip'}
O.bluebonnet((375, 900), 200, style="outline")                     # occluded, half-hatched line art
O.ripples(375, 525, 12, count=6); O.ripples(375, 525, 12, breaks=0)
O.LEAF_SHAPES.keys()
```

Sprays are painted in order with occlusion: later leaves hide what is behind
them (plus `gap`), and the stem stops at leaf outlines.

### ornament — radiance & patterns

```python
O.sunburst(375, 525, 20, 90, 32)                                   # style spike|line|wedge; arc=(a0,a1)
O.fan(60, 60, 90, 0, 90, 9, rims=(1, 0.8), hub=10)                 # Monarchs-style deco fan
O.starburst(375, 525, 60, 18, 8, layers=2)                         # faceted compass star
O.fleuron(375, 525, 50, style="lily")                              # lily|palmette|heart|scroll
O.fleuron(375, 525, 50, style="lily", line_style="outline")
shield = "M0 0H200V110C200 170 150 200 100 215C50 200 0 170 0 110Z"
O.diaper(shield, 18); O.scales(shield, 10); O.quatrefoil(shield, 28); O.stripes(shield, 5, 5)
O.ermine(shield, 28); O.chevrons(shield, 11, 7); O.checks(shield, 14, angle=45); O.polka(shield, 12, 2)
O.tile(shield, O.fleuron(0, 0, 20), 30, 34)                        # any motif on a half-drop grid
O.ermine_spot(0, 0, 10)
```

### suits — pips, layouts, indices, frames

```python
SU.pip("spade", 375, 525, 116)                       # field pip, placed by bounding-box centre
SU.pip("heart", 375, 470, 280, style="inline")       # styles: solid|outline|half|inline|engraved
SU.pip("club", 100, 100, 62, rot=180, geometry="classic")
SU.pip_shape("diamond", 100); SU.pip_size("spade", 62)          # (62.0, 68.2) — brief §E.1
[SU.pip("diamond", x, y, 116, rot=180 if r else 0) for x, y, r in SU.pip_layout(7)]
idx = SU.index("10", "heart")                        # rank + pip at both corners (brief §D.1)
cf = SU.court_frame()                                # {'outer','inner','band','window'}
SU.ace_keyline("heart", 375, 470, 280)               # gold keyline 10 px outside the pip
SU.suit_name("♠"), SU.SUITS, SU.RANKS
```

### heraldry

```python
sh = HR.shield(375, 520, 190, 230, "heater")          # heater|french|spanish|swiss|lozenge|roundel|oval
HR.tincture(sh, "azure")                              # or|argent|gules|azure|vert|purpure|sable|tenne|sanguine
HR.crown(375, 300, 150, style="royal")                # royal|ducal|mural|eastern; line_style="outline"
HR.TINCTURES
```

### typeset — outlined type

```python
from inkkit import typeset as TY
d, bbox, adv = TY.text_to_path("Cinzel", "SAN MARCOS", 40, 375, 100, anchor="middle",
                               baseline="alphabetic", variations={"wght": 700}, tracking=150)
TY.text_on_arc("Cinzel", "· SAN MARCOS ·", 16, 375, 525, 140, variations={"wght": 700}, tracking=120)
TY.text_on_arc("Cinzel", "TEXAS", 16, 375, 525, 140, bottom=True)
TY.text_on_path("EBGaramond", "river", 18, "M100 700 C 300 600 450 800 650 700", offset=3)
TY.measure("Cinzel", "SAN", 40); TY.font_metrics("Cinzel"); TY.resolve_font("EBGaramond[wght]")
TY.load_font("BodoniModa", {"wght": 800, "opsz": 60})
```

Fonts resolve by name in `<root>/fonts` (case-insensitive, literal, prefix
match preferring the exact stem, then the variable font, then `-Regular`).
Variable fonts are instanced (cached). Anchors: start|middle|end. Baselines:
alphabetic, middle (cap-height centre), top, x-middle, bottom. Tracking is in
1/1000 em. Characters a font lacks warn and draw as .notdef (`missing="raise"`
to fail); control characters such as `\n` are skipped with a warning (one line
per call); combining marks are not shaped — use precomposed characters.

### card — composition, rendering

```python
card.W, card.H, card.R, card.CX, card.CY, card.SAFE, card.BLEED
card.card_outline_d(); card.inset_outline_d(30)
half = svg.path(G.star_d(375, 300, 80, 30, 5), fill=T.RED)
court = card.two_headed(half, divider="h", box=(60, 60, 630, 930))   # one shared <clipPath>
card.rot180(half); card.mirror(half); card.clip_group(half, card.card_outline_d(40))
doc = card.new_card(); doc.add(court, card.safe_zone(), layer="ink")
card.clip_group(half, card.card_outline_d(40), doc=doc)              # ids from doc.uid (else a content hash)
doc.save("/tmp/court.svg"); card.render("/tmp/court.svg", "/tmp/court.png", 750)   # RuntimeError on failure
card.contact_sheet(["/tmp/court.png", "/tmp/quick.png"], "/tmp/sheet.png", cols=2, round_corners=True)
```

### preflight — will it print?

```python
rep = PF.preflight(doc, "ink_offset", profiles={"foil": "foil"}, overlay="/tmp/pf")
print(PF.summary(rep))            # per plate: ink area, % too thin, % plugging, node count
PF.preflight_svg(open("/tmp/sep-ink.svg").read(), "ink_offset")      # any single-ink SVG
PF.node_count(doc.to_string())
```

Each plate is rendered at 4× (1200 ppi) and measured with a morphological
opening (features thinner than `min_line`) and closing (gaps narrower than
`min_gap`). The overlay PNG shows ink grey, too-thin red, plugging blue.
Crossing hatch and guilloché always leave a few tiny plugging interstices at
their crossings; look at the overlay rather than the percentage alone.

## Known limitations

* Geometry from booleans/strokes is dense polylines (0.01 px grid);
  `fit=`/`fit_curves` refits them with Béziers within tolerance.
* Kerning reads GPOS pair adjustment (formats 1/2) and legacy `kern`; no
  shaping (ligatures, contextual alternates, mark positioning).
* `flow()` and `stipple()` are pure Python (a full card takes ~5–8 s).
* Separations expand `<use>` of defs but not symbols with their own
  `viewBox`; trap chokes only path fills and stroke widths.
* Ornament generators are parametric starting points, not finished art — the
  deck's figurative work (courts, aces) still needs bespoke centrelines.
