# deck.motifs: HEADWATERS ornament library

This is the shared line-art vocabulary for the cards, back, tuck and seal. It
covers the §G geometric motifs of `research/creative-brief.md` and the helpers
that the figurative motifs (Lion Mark, darter, wild rice and the rest) build on.

```
deck/motifs/
  core.py        Frag/Mark model, legal strokes, terminals, Turtle (exact tangent arcs),
                 hatch / half_hatch, knockout, cut / interlace, clip, C2 / D2 symmetry, bubbles, QA
  geometric.py   the §G geometric motifs (rosette, running wave, strata, lens field, ...)
  forms.py       (B2) figurative constructions: arc splines / biarcs, curved-midrib leaves,
                 scallop / lock / tuft rows, tight-spot QA
  lion.py        (B2) §G.2 Lion in moleca (fitted to a silhouette) + simplified Lion Mark,
                 §G.3 Lion andante, the spring vent
  rice.py        (B2) §G.4 ribbon leaf, §G.5 flowering stalk, §G.6 wreath
  fauna.py       (B2) §G.15 gill plume, §G.25 fountain darter, Texas blind salamander (seal)
  hair.py        (B2) §G.24 current lines (+ flat-gold locks)
  sheet.py       specimen sheets and back-scale knockout test → build/motifs/
  sheet_figurative.py  (B2) the figurative sheet + in-context renders
  test_motifs.py / test_figurative.py   rule checks (plain asserts)
```

```sh
.venv/bin/python -m deck.motifs.sheet             # both sheets (geometric + figurative), cells/, back-test-*, reports
.venv/bin/python -m deck.motifs.sheet figurative  # only build/motifs/sheet-figurative.png + fig-*.png contexts (≈25 s)
.venv/bin/python -m deck.motifs.test_motifs       # 12 rule checks (≈5 s)
.venv/bin/python -m deck.motifs.test_figurative   # 13 figurative rule checks (≈12 s)
```

## Conventions (read first)

* **Units and angles.** Units are card px (750 × 1050, 300 ppi), with y pointing down.
  Angles are **screen degrees**: 0 = +x, 90 = down, and positive rotation is clockwise on screen.
  `DIAG = -45` is the brief's "45°" hatch, drawn rising to the right ("/").
* **Final size only.** Every motif is generated at the size it will print.
  * Nothing is ever scaled.
  * `Frag` accepts only rigid transforms: translate, rotate, and ±1 mirrors.
    A scaling matrix raises an error.
  * Transforms are applied to the path data, so no SVG `transform` is ever emitted.
* **Legal strokes only.** `stroke()` rejects any width outside
  {1.6, 2.1, 3.1, 4.2, 6.25}. The default is FINE (2.1).
* **Caps and joins** use the presets in `STYLES` (§B.2):
  * `ornament`: round caps, round joins.
  * `hatch`: butt caps.
  * `rule`: butt caps, miter joins, miterlimit 4 (frames, fault-steps, ashlar, arcades).
  * `point`: miter joins, miterlimit 10 (vesicas, kites, compass points).
* **Colour selects the layer.** Passing a palette token picks its print layer:
  * INK goes to `ink`, RED to `red`, JADE to `jade`, FOIL to `gold`, PAPER to `paper`.
  * `Frag.layers()` returns `{layer: svg}` in the brief's order: paper, jade, red, gold, ink.
* **Diameters.** A ring bubble's Ø is its *centreline* diameter. A dot's Ø is its filled diameter.
  Dots use Ø 4.2, 6.3 or 8.4, and every free-end terminal is a Ø 6.3 solid dot.
* **Spacing.**
  * Defaults keep at least 4.2 px clear between parallel strokes (§I.12).
  * Where the brief itself forces less, the motif records it in
    `frag.meta['warnings']`. It still builds.

### The Frag: one object, two drawing modes

```python
from deck.motifs import *                     # or: from deck.motifs import core as C, geometric as M
from deck import tokens as T

f = source_rosette(375, 525, 130)             # a Frag: a list of Marks (stroke or fill, colour, layer)
f.layers()                                    # LINE mode: {'ink': '<path .../>...'} per print layer
knockout(flood_d, f)                          # KNOCKOUT mode: flood minus the exact union of the marks -> FILL d
reversed_out(flood_d, f, color=T.JADE)        # the same, wrapped as a jade fill Frag
```

* `f.outline()` is the exact union of the marks as FILL d. Strokes are expanded by skia-pathops
  with their own width, cap and join, so knockouts are geometric, never paper-coloured paint.
* `f.shape()` is the same outline as shapely geometry.
* `f.to_fill()` returns the marks as fills.
* `f.bbox()` gives the bounding box.
* `f.meta` holds construction facts and warnings. Examples: `rosette`, `n_waves`, `hull` (conduit), `exit` (volute).

## core.py API (one line each)

| function | example |
|---|---|
| `stroke(d, w=FINE, style='ornament', terminals=None, color=INK)` | `stroke("M0 0 C 40 -20 80 20 120 0", terminals="both")` |
| `fill(d, color=)` | `fill(lozenge_d(0, 0, 20, 12), color=T.FOIL)` |
| `dot(x, y, d=6.3)` / `terminal(x, y)` / `ring(x, y, d)` | `dot(10, 10, 4.2, color=T.RED)` |
| `with_terminals(d, 'both')` | `with_terminals("M0 0L60 0")` returns Ø6.3 dots on the free ends |
| `Turtle(x, y, heading)`: `.fd(L)`, `.arc(r, sweep)`, `.line_to()`, `.jump()`, `.d()`, `.pts()` | `Turtle(0, 0, 0).arc(11, -90).arc(9, 180).d()` builds tangent arcs with exact `A` output |
| `arc_d(cx, cy, r, a0, a1)` / `arc_between(c, r, p, q, cw)` / `ellipse_arc_d(...)` | `arc_d(0, 0, 50, 180, 360)` draws the upper semicircle |
| `vesica_d(p0, p1, width)` / `lozenge_d(cx, cy, L, W, rot)` / `polyline_d(pts)` | `vesica_d((0, 60), (0, -60), 44)` |
| `hatch(region, angle=DIAG, pitch=7, origin=None)` | `hatch(box(0, 0, 40, 12))` gives FINE butt-capped hatch, centred in the region |
| `half_hatch(shape, split, angle, side=)` | `half_hatch(leaf_d, "left", "perp")`; `split` may be 'left'/'right'/'top'/'bottom', a 2-point line or an S-midrib path |
| `split_region(shape, split, side)` | `split_region(kite, [(0, 0), (0, 64)], side=-1)` |
| `hatch_lines(region, angle, pitch, origin=)` | the raw polylines, when you need them |
| `knockout(solid_d, *frags, grow=0)` | `knockout(G.rect_d(37.5, 37.5, 675, 975, 18), back_frag)` |
| `cut(frag, obstacle, gap=4.2)` | `cut(rules, roundel, 4.0)` breaks the rules 4 px clear (round caps allowed for) |
| `interlace(under, over, gap=4.2)` | `interlace(stroke(s2), stroke(s1))` returns `cut(under, over) + over` |
| `clip(frag, region, inside=True, keep_caps=False)` | `clip(pattern, bodice_d)` |
| `c2(f)` / `cn(f, n)` / `d2(f)` / `bilateral(f)` / `mirror_x` / `mirror_y` / `rot180` | `c2(bubble_triad(525, 295))` places the 180° copy about the card centre |
| `bubble(x, y, d, style='auto')` | `bubble(0, 0, 7)` draws a ring (hole ≥ 3 px); `bubble(0, 0, 4)` draws a dot |
| `bubble_row(p0, p1, sizes)` | `bubble_row((0, 60), (0, -40), bubble_sizes(3, 7))` spaces them with equal clear gaps and raises if a gap < 3 |
| `bubble_path(path, d0, ratio=1.2, gap=None, n=None)` | `bubble_path("M0 0 C 20 -40 0 -80 30 -120", 3)` |
| `bubble_triad(x, y, angle, sizes=(4.2, 6.3, 8.4))` | `bubble_triad(0, 0, -45, (6.3, 10.5, 6.3), style="ring")` is the ♥ house mark |
| `dashes(pts, on=8, off=6)` | builds geometric dash pieces, so renderers and knockouts agree |
| `check(frag)` | lists illegal widths, colours or layers (empty means clean) |
| `knockout_report(solid, ko_d, min_line, min_gap)` | a raster opening test that returns coverage plus the areas of too-thin lines and gaps |
| `polar_map(cx, cy, r_base)` / `strip_map(uv, frame)` / `sample_d(d)` | bend a strip motif onto a ring; dense polylines |

## geometric.py API (brief §G)

| § | function | example / notes |
|---|---|---|
| 1 | `source_rosette(cx, cy, R=130, twist=True, detail=None)` | See **Source Rosette** below. |
| 1 | `rosette_spec(R, w, detail)` | the band recipe (radii) |
| 1 | `crater(cx, cy, r, n=8, hub=8, twist=30)` | the rosette's centre part, also usable on its own |
| 1 | `rib_band(cx, cy, r0, r1, n=24, twist=25, hatch_cells='alternate')` | the rosette's rib band, also usable on its own |
| 1 | `bubble_ring(cx, cy, r, n, d)` / `concentric_rings(...)` | the rosette's bubble and plain rings, also usable on their own |
| 7 | `wave_hook(height=20, a=None)` | One hook in local coordinates. See **Running wave** below. |
| 7 | `running_wave(x0, x1, y, height=20, pitch=30, flow=±1, up=±1)` | `running_wave(100, 340, 91.5)` |
| 7 | `running_wave_d2(cx, y, half_len, gap=36)` | Mirrored at the axis, flowing outward. The back's top band is `running_wave_d2(375, 91.5, 260, gap=36)`. |
| 7 | `running_wave_ring(cx, cy, r_base, n=None, r_limit=None, mirrored=False)` | Rigid hooks springing outward, clockwise. `mirrored=True` gives the D2 version: waves flow from 12/6 o'clock toward 3/9, where a Ø6.3 dot receives them. |
| 8 | `ripple_rings(cx, cy, r0, gap0, n=3, ratio=1.3, ry_ratio=1, arc=None, mode='offset'\|'similar')` | `ripple_rings(375, 994, 60, 30, ratio=1, ry_ratio=8/60, mode="similar", arc=(0, 180))` (A♥) |
| 9 | `bubble_beading(p0, p1, d0=3, ratio=1.2, n=None)` | `bubble_beading((115, 480), (115, 260), 4, n=9)` |
| 10 | `fault_step(x0, x1, y, at=None, rise=4.5w, double=None)` | `fault_step(139, 611, 523, double=6.3)` |
| 10 | `fault_plinth(cx, y, width=60, steps=2, hatch_step=0)` | Stacked slabs with bedding lines, closed foot. `meta['top']` gives the top tread. |
| 11 | `strata(region, heights=(12, 19), hatched='thin', fault=((x, y), (x, y)), jog=None)` | `strata(mantle_d, fault=((300, 480), (420, 330)))`: the courses right of the fault drop one course |
| 12 | `karst_voids(region, sizes=(6, 10, 16), seed=1983)` / `karst_void(x, y, d)` | A hashed staggered grid that steps sizes down to keep 4.2 px clear. The Ø16 void carries a crescent inner offset. |
| 13 | `stalactite(x, y, length=64, width=20, hatch_side='left', rot=0)` | Hangs from (x, y). Rings sit on one half, hatch on the other. |
| 14 | `drip_fringe(x0, x1, y, pitch=12, l_min=8, l_max=26, periods=1)` | `drip_fringe(400, 520, 460)` |
| 16 | `scale_lattice(region, r=10, step=0.6)` | `scale_lattice(bodice_d, 10)` |
| 17 | `cypress_knee(x, y, h, base_w=34, hatch_side=None)` | a single knee |
| 17 | `knee_crenellation(x0, x1, y, h=40, heights=(.65, .8, 1, .8, .65))` | `knee_crenellation(290, 460, 150, h=50)` |
| 18 | `comb_spray(path, pitch=7.5, tick=9, angle=55, cone=None)` | `comb_spray("M375 250 L375 118", cone=11)` |
| 18 | `cypress_cone(x, y, r)` | a circle with 4 inward-bowed scale arcs |
| 19 | `reed_ladder(p0, p1, width=16, rung=26, node_every=4, rails=True)` | On the back, span the band: `reed_ladder((68.5, 106), (68.5, 944), width=22, rails=False)` |
| 19 | `reed_node(x, y, stalk=7, tick=8)` / `reed_node_medallion(x, y, d=26, rot=0)` | the ♣ house mark (≈26 px, C2) / the side-band medallion |
| 20 | `ashlar(region, block=(42, 18), joint=7, chamfer=3)` | `ashlar(tabard_d)` |
| 21 | `arch(x, y, span=30, jamb=12, key=(7, 22), ring=6.3)` | a single arch |
| 21 | `arcade(x0, x1, y, span=30, pier=None)` | Piers are auto-widened so that neighbouring extrados rings keep 4.2 px clear. `ring=None` gives single-line arches. |
| 22 | `rowel_star(x, y, r_out=40, points=8, hub=9, lengths=(1,), hatch_side=-1, solid=False)` | Compass rose: `lengths=(1, .6)`. Small gold rowels on red: `solid=True`, then give it an Aquifer contour yourself (§C rule 4). |
| 23 | `stepping_stones(x0, x1, y, band=18, pitch=24, stone=(12, 7), centre=(22, 13))` | The rails break 4.2 px clear of a tall centre stone. |
| 26 | `lens_geometry(cx=375, top=104, bottom=946, width=540)` | Returns R = 463.2, centres (181.8, 525) and (568.2, 525), and d. |
| 26 | `lens_cartouche(geo, inner=6.3)` | the lens rule plus a parallel rule inside it |
| 26 | `lens_field(geo, count=7, pitch=11, clip_to=, corners=, solid=2)` | HAIRLINE offsets that turn to 8/6 dashes progressively toward `corners` |
| 27 | `vent_roundel(x, y, d=56, inner_d=16, ribs=12)` | `vent_roundel(68.5, 74.5)` |
| 28 | `festoon(supports, sag=18, bulb_d=6.3, drop=0)` | `festoon([(180, 380), (300, 380), (420, 392)], sag=22)` |
| 29 | `pearl_beading(path, d_min=4.2, d_max=8.4, n=None, gap=3.5)` | `pearl_beading("M150 300 A 200 200 0 0 1 600 300")` |
| 30 | `conduit(path, width=14, d0=3, ratio=1.2, n=None)` / `conduit_break(f, conduit, gap=4)` | `conduit_break(strata_f, c)` removes everything within the band plus 4 px |
| 31 | `volute(x, y, r0=12, heading=-90, cw=True, turns=1.0)` | `meta['exit']` is the tangent branch point |
| 31 | `tooled_scroll(x0, x1, y, height=40, n=None)` | A running spiral for ♦ cuffs and belts only. |

### Source Rosette

* **At R = 130 the radii are the brief's exactly:**
  * crater r20 with 8 curved ribs, a hub r8 and a Ø4.2 dot;
  * ripple rings at r30, 39 and 50;
  * a bubble ring at r62 (24 × Ø7);
  * a pinwheel band from r72 to 104 (24 ribs twisted 25° clockwise, alternate cells hatched);
  * a running-wave ring flowing clockwise;
  * an outer rule at r130.
* **Smaller R never squeezes a band.** The function picks the recipe designed at or below R, and recipes only ever scale up:
  * medium from R90;
  * small from R40 (the A♥ size at MEDIUM);
  * tiny from R16 (a jewel or finial).
* **`twist=False` gives the D2 variant.** Ribs become straight and the wave ring becomes the mirrored version.

### Running wave

* `wave_hook` builds one hook, springing tangentially from the rule:
  * a quarter circle (radius a) rises;
  * a semicircle (radius b) curls over the crest;
  * a second semicircle (radius b/2) turns the curl inward;
  * the Ø6.3 terminal "eye" lands exactly at the crest centre.
* The eye clearances are checked in `test_motifs`.

## Interpretations of the brief (decide once, documented here)

1. **Running wave (§G.7).** Each wave is a hook of a quarter-circle rising into a semicircle curl. It springs tangentially off the band's rule and ends in a Ø6.3 eye at the crest centre, satisfying the free-end terminal rule (§I.14). A single continuous line knotted at every trough, so the hook form was chosen.
2. **Rosette wave ring (§G.1, "r 110–124").**
   * The hooks spring from the pinwheel's r104 rule, because a separate baseline at r110 would sit 3.9 px from r104.
   * Their height is reduced automatically (to 17.3 px) so the crests keep 4.2 px clear of the r130 rule.
   * The hooks are rigid copies (C24), not strip-mapped, so every arc stays a true circle.
3. **Pinwheel ribs.** 24 ribs twisted 25° clockwise. Each is a circular arc through its two end points, with a sagitta of 0.14 × chord bowing counter-clockwise. That balances both rule junctions at ≈40°. The twist exceeds the 15° rib pitch, which gives the turbine sweep. Hatch runs as rungs across the cells.
4. **Lens inner rule (§H.19, "6 px inside").** Drawn at **6.3** px centre-to-centre (w + 4.2), because 6 px leaves only 3.9 px clear. It is overridable with `inner=`.
5. **Karst void inner offset (§G.12).**
   * A concentric FINE offset collapses at Ø16 (the ring would be ≈Ø3).
   * Instead the void's own contour is shifted by w + 4.2 and kept inside: a crescent line, 4.2 px clear at its crown, that meets the rim at both ends.
   * Voids are horizontal ellipses with height Ø and width 1.3 Ø.
6. **Stalactite (§G.13).** The 3 growth arcs sit on the un-hatched half, so hatch and arcs never cross. Detail stops where the half-width drops below w + 4.2, so the tip stays a clean point.
7. **Cypress cone (§G.18).** Four arcs join rim points 90° apart and bow inward. The result is a curved-square centre scale with four rim scales and no X crossings.
8. **Reed node (♣ house mark).** The ticks spring from the stalk on either side of the node, as in the ♣ divider. Ticks springing from the node itself line up into one stroke that skewers the ellipse.
9. **Fault plinth.** Bedding lines separate the slabs and the foot is closed, so any hatch ends on a line (§B.2: no hatch ending in mid-air).
10. **Bubbles.** `style='auto'` draws rings only when the hole stays ≥ 3 px (d − w ≥ 3). Otherwise it draws solid dots, so a Ø3→8 column is all dots.
11. **Festoon bulbs.** The brief's "Ø 5–6" bulbs become the legal Ø6.3 dot.

## Notes for Track B2 (figurative motifs)

* **Tangent-arc curves.** Build midribs, spines, S-leaves and the wing sickles with `Turtle`. It gives exact `A` output and guaranteed tangent continuity. `Turtle.pts()` feeds region and strip operations.
* **Leaves.**
  * The outline is `vesica_d(p0, p1, width)` with `style="point"`.
  * Add the midrib as a stroke.
  * Hatch one side with `half_hatch(outline, midrib_pts, "perp", side=±1)`. It accepts an S-shaped midrib (a polyline or d), extends it and keeps one side.
  * "perp" uses the chord of the split.
* **Current lines (§G.24).**
  * Offset a guide with `G.Curve(guide).offset(k * 7.0)` for k = 0…4 and stroke each line.
  * Add a terminal with `stroke(..., terminals="end")`.
  * Keep the pitch at 7 px or more, since w + 4.2 = 6.3 is the minimum.
* **Darter stitch line.** Use `dashes(pts, 7, 4)`. Any dash under 6.3 px with round caps becomes a dot; use `style="rule"` (butt caps) for crisp dashes.
* **Gill plume, spikelets and awns.** Use `stroke(..., T.HAIRLINE)` for awns only. HAIRLINE is never a contour.
* **Interlace.** Use `interlace(under, over)`. The under-stroke stays a stroke, cut 4.2 px clear of the over-stroke's outline. For a "passes behind" region, use `cut(f, region_d, gap)`.
* **Two-headed and C2 composition.** Use `f.rot180()` and `c2(f)`, which work about (375, 525). For courts, clip the top half with `clip(f, box(0, 0, 750, 525))` first.
* **Gold on red (§C rule 4).** Only as a solid shape with an Aquifer contour: `fill(sil, color=T.FOIL) + stroke(sil, T.FINE)`. Recolour a whole motif with `frag.recolor(T.FOIL)`.
* **Knockout lines inside solid pips (§B.2).** Build the motif at `w=T.MEDIUM`, then `knockout(pip_d, motif)`. Check the result with `knockout_report(pip_d, ko, min_line=2.5, min_gap=3.0)`.

## Known limitations

* **Clipped and cut strokes are polylines.** `cut`, `clip`, strata, ashlar and similar functions return dense polylines flattened at 0.01 px. Untouched motifs keep exact arcs. The result is visually exact, but files are larger.
* **Merged stroke paths.** `Frag.svg()` merges consecutive strokes that share a style into one `<path>`. That is fine for strokes. Each fill stays its own path.
* **Wave-ring height.** The rosette's wave-ring height depends on the brief's r104 and r130 radii; see interpretation 2.
* **Tight spacings the brief itself specifies.** These are warned about but still built:
  * the A♥ ripple ellipses ry 8 / 12 / 16 are 1.9 px clear on the minor axis;
  * a conduit 12 px wide with Ø6 bubbles leaves 2 px to the rails;
  * the ♠ divider double lines 6 px apart at MEDIUM leave 2.9 px clear;
  * the back's Ø56 vent roundel at (68.5, 74.5) leaves about 1.95 px of jade between its outer edge and the flood edge (under the 3 px knockout gap).
* **Karst void sizes.** The generator picks sizes by a deterministic hash and never places a void closer than 4.2 px. Density depends on `pitch`.
* **Lens field clipping.** `lens_field` clips to whatever region you pass. Exclude the plinths, roundels and emblem clearances with `region(...).difference(...)` before calling it.
* **Tooled scroll.** It is designed for bands 28–48 px tall. Below about 30 px, r0 < 8.4 and the eye loses its 4.2 px clearance, which triggers a warning from `volute`.
* **Back test coverage.** `sheet.back_test()` is an integration test, not the back design. Its coverage (~11 %) excludes the darters, wild-rice pinwheel and comb sprays, which will lift it toward the 18–22 % target.

---

# Figurative motifs (Track B2)

Same conventions as above: final size, legal widths only, colour picks the layer,
rigid moves only, `frag.layers()` for line mode, `knockout(solid, frag)` for knockout
mode. The lion, the salamander and the mark default to **gold** (`T.FOIL`); the darter,
rice and current lines to **Aquifer**; the gill plume to **Gill Red** — pass `color=`
(or `frag.recolor(...)`) for anything else. Every function below returns a `Frag`.

```python
from deck.motifs import *                      # everything below is exported
from deck.motifs import forms                  # construction helpers (module, not *-exported)
```

## lion.py (§G.2, §G.3, §H.13, §H.20)

| function | example / notes |
|---|---|
| `lion_moleca(cx=375, cy=262, silhouette=None, wing=WingSpec(), vent=None, paws=True, ears=True, pupils=True, face_r=30, color=T.FOIL)` | The FULL Lion in moleca for the A♠. `silhouette` (FILL d or shapely) is what the wings are fitted inside — default `deck.frames.ace_pip_d('S')`. `lion_moleca()` draws the A♠ lion as the brief places it. |
| `lion_moleca_parts(...)` | Same, as `{'face','ears','mane','paws','wings','vent','meta'}` — already occluded against each other, for re-stacking / recolouring. |
| `WingSpec(clear=12, root=76, wrist=46, fan=(...), p1_end=-12, curl_r=6.3, tip_axis=5.5, rows=(...), ...)` | The fitting knobs (angles are screen degrees about the head centre). The A♠ artist tunes these, never coordinates. |
| `moleca_wing(sil, head, mane_sil, obstacles, spec)` | One (right) wing; the left is its mirror. |
| `lion_mark(cx, cy, size=40, style='line'|'solid', detail=None)` | SIMPLIFIED Lion Mark, `size` = overall width (≤ 60). `style='solid'` is the clasp: flat gold silhouette + Aquifer contour and details — the only legal form on red (§C rule 4). `meta['strokes']` ≤ 24. |
| `lion_andante(cx=0, cy=0, lens=(330, 440), far_wing=True, ledge=True, ripples=True, clip_lens=True)` | §G.3 lion for the tuck lens, drawn about the lens centre. For the tuck front: `lion_andante(384.5, 540)`. |
| `spring_vent(cx=375, cy=350, rx=80, ry=16, rings=3, ribs=12)` | The A♠ vent; `meta['rim'](x)` gives the rim's top. |
| `lion_face`, `lion_ears`, `mane_rings`, `lion_paws`, `shingle_rows`, `drop_specks` | The parts, reusable (e.g. a lion-face brooch at `r=12`). |

**How the moleca is fitted.** The wing's leading edge is the silhouette inset by
`clear + w/2` (so stroke edges keep §H.13's 12 px). From `root` (behind the vent) it runs
round the lobe to the wrist; three shingled covert rows line it; four primaries fan up
into the lobe from the wrist, each ray-cast to stop `tip_gap` px short of the mane, vent,
paws or edge; the leading primary rides the edge and tapers out at `p1_end`, where the
mane closes in; the edge then sweeps on alone up the spade's upper edge and ends in a
§G.7 wave-hook curl (Ø6.3 eye) pointing in toward the apex, stopped `tip_axis` px short
of the axis. Nothing is hard-coded to one spade: `sheet-figurative.png` shows the same
call on Track A's live pip and on a spade rebuilt from the §H.13 table.

## rice.py (§G.4–6)

| function | example / notes |
|---|---|
| `ribbon_leaf(x, y, heading, length=140, width=None, ratio=11, bend=(14, -14), hatch=1)` | S midrib of two tangent arcs, vesica profile, one half hatched PERPENDICULAR to the midrib at every station. |
| `rice_stalk(x, y, heading=-90, length=170, n_female=6, n_male=4, spikelet_len=14, awn=13, bend=0)` | Erect female spikelets (3:1, ±15°, HAIRLINE awns) above; drooping male florets (±150°) below. `meta['female'|'male']`. |
| `rice_wreath(path, axis=375, pitch=40, leaf_len=90, ratio=13, bend=(12, -5), tip='spike')` | `path` = ONE branch, knot → tip; mirrored about `axis`, tied with a reed-node knot. Follows any path (the tuck's lens contour). |
| `rice_wreath_arc(cx, cy, r, knot_deg=90, tip_deg=30, step_deg=14)` | The A♣ half-arc (4 → 8 o'clock), pairs every 14°. |
| `spikelet(base, axis_deg, length=14, awn=0)` | One vesica spikelet (+ awn). |

**Tuck recipe (§H.20 items 4–5):** `deck.motifs.sheet_figurative.tuck_lens_demo()` places
`lion_andante` in the 330 × 440 lens and wraps the lower two-thirds with
`rice_wreath(lens_wreath_path(geo, 26, 0.66), axis=0, pitch=58, leaf_len=110, ratio=12)`, the
lens rule breaking 4.2 px round the leaves; translate by (384.5, 540) for the 769 × 1069 panel.
The swallowtail ribbon at the knot is the tuck designer's.

## fauna.py (§G.15, §G.25, seal)

| function | example / notes |
|---|---|
| `gill_plume(path, n=7, barb=(11, 4.5), angle=52, side=1, color=T.RED)` | Curved spine, 6–8 barbs on one side shortening to the tip, Ø4.2 tip dot. |
| `fountain_darter(x, y, length=100, facing=±1, rot=0)` | Centred at (x, y). C2 pair on the back's orbit: `d = fountain_darter(x, y, 100, rot=a); d + d.rot180()`. |
| `blind_salamander(cx, cy, radius=74, arc=255, head_deg=-50, tighten=0.06, rot=0)` | Dorsal view, curled in one C, auto-centred on (cx, cy); ≈ 190 px across (fits the seal's field inside its text ring). |
| `DARTER`, `SALAMANDER` | The design tables (tune drawings there). |

## hair.py (§G.24)

| function | example / notes |
|---|---|
| `current_lines(guide, n=4, pitch=7, side=1, stagger=9, terminals='end', gold=None|'alternate'|'lock')` | 3–5 offsets of one guide at 7 px, Ø6.3 terminals staggered so neighbours keep 4.2 px clear; `gold` fills alternate strips or the whole lock in flat gold (hair locks, §C rule 1) under Aquifer lines. |
| `lock_band(a_pts, b_pts)` | FILL d of the strip between two current lines. |

## forms.py (construction helpers)

`arc_spline(points, h_start, h_end, headings={})` (smooth G1 chains of circular arcs through
points — the backbone of every figurative curve), `biarc`, `biarc_chain`, `arc_path`
(turtle turn lists), `leaf(mid_pts, width | hw=, hatch=±1, rake=None|deg)` (a leaf / feather /
spikelet on a curved midrib; `rake` switches to feather barbs: parallel hatch leaning to the
tip), `vesica_hw`, `leaf_edges`, `perp_hatch`, `scallop_arc`, `scallop_ring`, `scallop_row`,
`lock_row`, `tuft_row`, `tight_spots(frag, 4.2)` (raster QA: ground narrower than 4.2 px),
`unit`, `rot`, `along`.

## Interpretations (B2, decided once)

1. **Mane, frontal (§G.2).** Three independent scalloped rings at the brief's peaks r 36 /
   48 / 60, alternate rings offset half a scallop; cusps 5.7 px inside each peak so each ring
   clears the next ring's cusps by exactly 4.2. Shingled rings (cusps on peaks) read as a
   sunflower; these read as layered locks.
2. **Frontal face.** A frowning brow runs into the nose bridge and an inverted-trapezoid
   nose pad (the "trapezoid nose"); the upper lip droops (dignified, never a smile); round
   ears on the face circle. Pupils touch the lids (face-kit convention).
3. **Wings of the moleca.** On Track A's spade the mane (r 60) comes within ≈ 2 px of the
   12 px inset at the shoulders, so the wing cannot pass beside it: it lives in the lobes
   (coverts + a fan of primaries rising toward the mane) and only its leading edge sweeps
   up the upper edges, passing the mane at exactly 4.2 px, before curling inward. The
   primaries' hatch RAKES toward the tip (feather barbs); perpendicular rungs on 5:1
   feathers read as ladders.
4. **Paws on the vent.** The forepaws rest on the vent's outer rim and pass in front of the
   lower mane (the mane breaks 4.2 px round them); the forelegs rise behind the face circle.
5. **Lion Mark.** A wing silhouette (arm + three pointed feather tips + two shafts) reads as
   a wing at 24–60 px; arcs with radiating vesicas read as laurel, strokes as antlers.
   Detail tiers by size (full ≥ 50: pupils; badge 34–50; tiny < 34: no face details or
   shafts). The **solid** clasp is the form for red grounds and for ≤ 40 px.
6. **Andante mane (§G.3 "scalloped arcs").** In profile, round scallops read as fleece. The
   mane is arc-built pointed flame locks fanned from behind the face, which read as mane.
   Round scallops remain on the wing's coverts.
7. **Andante water.** The hind legs wade: everything below the top ripple is hidden, so the
   legs stop 4.2 px above it. The ledge is three courses (12 / 19 / 12); the two thin
   courses are hatched at 45° (§G.11's alternate-course hatch) and the scarp face drops
   to the water line.
8. **Wild-rice ribbon leaf.** The full G.4 construction (midrib + half-hatch) needs the
   un-hatched half to keep 4.2 px clear, i.e. a leaf ≥ 12.6 px wide (≥ 126 px long at 10:1).
   Narrower leaves (the wreath's) are plain vesicas; `meta['warnings']` says so.
9. **Flowering stalk (§G.5).** A 6 px pedicel at ±15° cannot carry a 3:1 spikelet clear of
   the stalk, so the pedicel spreads (70° female / 95° male) and the spikelet's own axis
   stands at ±15° (erect) or ±150° (drooping). Same-side pitch keeps each awn clear of the
   next spikelet.
10. **Wreath tips.** Each branch ends in a short flowering spike (three erect spikelets with
    awns) so the wreath can never read as laurel (§G.6 "no laurel or olive").
11. **Darter at 100 px.** 9 fanned spines can only reach 5 px spacing at their tips (the fan
    converges toward its hidden pivot); the saddle bars stop 3.0 px (knockout minimum)
    above the stitch dashes, because at 16.7 px deep the body cannot hold saddle + 4.2 +
    stitch + 4.2 + belly; the stitch stops at x 36 % so all 8 saddles fit. The caudal fin is
    split on its axis with the upper half hatched.
12. **Blind salamander.** Dorsal view (the only view that shows both vestigial eyes, all
    four limbs and both gill trios). Limbs are thin jointed tubes (outlined, never stick
    legs — a stick-legged curled lizard reads as a petroglyph, san-marcos.md §6); the limb
    inside the C is posed differently from its outer twin so it never crosses the gills;
    gills lie over the fore-limbs (interlace).

## Changes to B1's files (backwards-compatible)

* `core.Frag.fragments()` / `core.Frag.items()` — a Frag can be returned wherever a
  `{layer: [svg]}` dict is expected, so Track A's `deck.frames.lion_mark_fragments` hook
  (which looks up `deck.motifs.lion_mark`) works unchanged.
* `sheet.layered_svg(..., under=[(d, colour)])` preview underlays; `sheet.build_cell(i, spec,
  prefix='')` honours optional `spec['ground'|'under'|'view']`; `sheet.compose(..., title=,
  sub=)`; `sheet.main(argv)` builds `geometric`, `figurative` or both.
* `__init__.py` also exports the lion / rice / fauna / hair names.

## Known limitations (B2)

* **Track A's spade ≠ the §H.13 table.** `ace_pip_d('S')` today is 306 px wide (lobes at
  y ≈ 345, width 217 at y 262) where the table says 340 / 250. The moleca refits to either;
  on the narrower spade the mane leaves no room beside it at the shoulders (interpretation 3).
* **Brief-forced tight spots**, all reported by `report-figurative.txt`: the vent's 3 rings
  at ry 16 are 2.4 px clear on the minor axis; the darter's fin spines converge at their
  pivot; converging V-junctions at every leaf tip, spike base and feather tip.
* **Lion Mark at ≤ 32 px** is a winged roundel rather than a readable face — use the solid
  clasp there.
* **Andante** is the least resolved drawing: the body and legs are sound but plain (no
  interior modelling beyond shoulder and thigh lines), and the far wing shows only as
  primaries behind the near wing.
* **Files:** occluded (cut) parts are dense polylines; untouched parts keep exact arcs.
* **Renderer agreement (§I.25):** rsvg-convert and resvg agree to anti-aliasing (the tuck
  context: 13 pixels differ by ≤ 27 %, all at needle-sharp miter-10 leaf tips). Mane and
  tuft locks use round joins for that reason.
