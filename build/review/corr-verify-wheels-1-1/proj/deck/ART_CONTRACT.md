# HEADWATERS art contract

How one piece of art (a court, an ace, a joker or the card back) plugs into
the deck system. The system (Track A) owns `deck/pips.py`, `deck/index.py`,
`deck/cardsvg.py`, `deck/layout.py`, `deck/frames.py`, `deck/build.py`,
`deck/qa.py`, `art/`, `cards/` and `build/`. The ornament library
(`deck/motifs/`) is Track B's. The creative brief
(`research/creative-brief.md`) is law; section numbers below refer to it.
Where the system departs from the brief, §10 lists each deviation and why.

---

## 1. One module per piece

Each piece is a Python module `art/<ID>.py`:

| Kind | IDs | File written |
|---|---|---|
| Courts | `KS QS JS KH QH JH KC QC JC KD QD JD` | `cards/KS.svg` … |
| Aces | `AS AH AC AD` | `cards/AS.svg` … |
| Jokers | `JOKER_RED` (Big, the Fool), `JOKER_BLACK` (Little, the Trickster) | `cards/JOKER-RED.svg`, `cards/JOKER-BLACK.svg` |
| Card back | `BACK` | `cards/BACK.svg` |

The tuck box and seal live under `tuck/`, not here.

A module exposes one function:

```python
def build() -> dict[str, list[str] | str]:
    """{layer: [svg fragment strings]} in card coordinates."""
```

- The keys are layer names: `paper`, `jade`, `red`, `gold`, `ink`. Omit the empty ones.
- The values are SVG element strings, such as `<path d="…" fill="#1D5A55"/>`, or one string per layer. A Track B `Frag` gives this directly: `frag.layers()` returns `{layer: str}`. Merge several dicts with `deck.cardsvg.layers_merge(a, b, …)`.
- Use plain `<path>` (or `<circle>`, `<ellipse>`, `<rect>`, `<line>`, `<polyline>`, `<polygon>`) inside optional `<g>` groups. See §4 for what is banned.
- `build()` must be deterministic and must not write files.
- A court module may set `CUT_Y` (see §3.1).

When a module is missing, or raises an error, the piece builds as a placeholder (frame or pip only). The deck therefore always builds, and the traceback is printed.

## 2. Coordinates and layers

- Card space is `viewBox 0 0 750 1050` in px, with y pointing down. The centre is (375, 525) and the corner radius is 37.5. Poker size at 300 ppi, so 1 pt = 4.17 px.
- The safe zone is inset 37.5 px. No type and no critical art may sit outside it; the only exception is the back's flood edge, which lies exactly on it.
- Every card SVG has exactly five layer groups. They print (and paint) from bottom to top: `<g id="paper">`, `jade`, `red`, `gold`, `ink`. The one exception is **A♠ and A♣**, which use `paper, jade, red, ink, gold`, because §K puts the gold emblem above the Aquifer silhouette.
- Put a colour's fills and lines on that colour's layer. Fills sit below lines **of the same layer** if you list them first.
- Within a layer, the system's elements are drawn **after** yours. The band rules, frame and indices therefore sit on top of the art.

| Colour | Hex | Layer |
|---|---|---|
| Limestone (stock) | `#F4EFE3` | `paper` only. The system paints the stock. |
| Spring Jade | `#1D5A55` | `jade` |
| Gill Red | `#AE2F2B` | `red` |
| Lion Gold (flat) | `#B08D57` | `gold` |
| Aquifer | `#15242B` | `ink` |

Import the colours from `deck.tokens` (`T.JADE`, `T.RED`, `T.FOIL`, `T.INK`, `T.PAPER`). Never hard-code them.

### 2.1 The layer trap: a lower plate never shows through a higher solid

Layer order is paint order, whatever order you write your fragments in. On every piece except A♠/A♣ the order is **paper < jade < red < gold < ink**, so:

- a **gold** eye ring, a **jade** hatch tract or a **red** detail drawn over an **Aquifer solid** is invisible (ink prints on top of it);
- **jade** or **red** drawn over a **gold** solid is invisible; **jade** drawn over **red** is invisible.

When a lower-layer colour must show inside a higher-layer solid, **cut it out of the solid** — the solid gets a hole exactly where the lower colour is, plus the §5 gaps:

```python
from deck import motifs as M
body = M.knockout(body_d, eye_ring_frag, grow=0.0)       # FILL d with the ring's shape removed
# or: body = G.difference(body_d, G.outline(ring_d, T.FINE))   (+ G.offset(..., gap) for clearance)
```

Example: the Little Joker (§H.18) is an Aquifer body with a gold eye ring and jade half-hatched feather tracts; the body must be cut where the ring and the tracts are. QA check **4c** warns about lower-layer marks sitting inside a higher-layer solid (anything wider than a CONTOUR line), and marks them orange in `build/qa/flags/<stem>.png`.

## 3. What you draw and what the system adds

### 3.1 Courts: draw the TOP HALF only

- Draw inside the **art window**: x 139–611, y 55–511. This is the frame offset 11 px inside, with chamfered corners. `deck.frames.art_window_d()` gives the exact outline.
- Attributes may run past y 511, toward 525; the system clips them.

The system then adds:

1. **Clip.** Each layer is clipped to `frames.court_clip_d(rank, CUT_Y)`: the chamfered art window above `CUT_Y`, minus the rank medallion's mask disc.
   - The disc's radius is the medallion's outer edge plus 4.2 px: **K 33.25, Q 27.25**, J none.
   - The default `CUT_Y = 511` puts the cut on the band's top rule. The band then reads as a clean paper strip that hides the cut (§F.1).
   - Set `CUT_Y = 525` in the module only if an attribute must visibly cross the band. The band rules and partition line are then drawn over your art, and QA check 12 measures the gaps between them.
2. **The 180° copy** about (375, 525), one per layer (`cardsvg.two_headed`).
3. **The frame.** The outer RULE Aquifer chamfered rule and the FINE gold inner rule 7 px inside it.
4. **The divider band.** Two FINE rules at y 511 and 539, the MEDIUM house partition line and the rank medallion:
   - ♠ fault-step: a double line (7.3 apart) stepping one course (7.1) at x 375 — `frames.RESOLUTIONS["fault_step"]`;
   - ♥ ripple (λ 44, A 5, odd about x 375, x 144–606); ♣ reed (stalk, nodes every 96, leaf pairs every 48, springing from the nodes); ♦ ford (rules at 520/530, lozenge stones every 40);
   - **King:** Ø 56 FINE Aquifer ring + FINE gold ring 6.3 inside + the gold house mark (≈ 26 px);
   - **Queen:** Ø 44 FINE Aquifer ring (Ø 46.1 overall) with 8 gold beads Ø 4.2 inside it (r 15.85, at 22.5° + 45° k) and the compact gold house mark (≈ 20 px).
5. **The corner pips.** u 88, top at y 62, centred on x 190, plus the rotated copy. `frames.corner_pip_d(suit)` gives the path. The ♠ corner pip runs to y 169.4 (D1).
6. **The indices.**

Keep the figure and its attributes **≥ 12 px** clear of the corner pip (QA check 10c measures it on the vector geometry). Put tall attributes on the viewer's **right** (§H.0). The simplified Lion Mark hallmark: `frames.lion_mark_fragments(cx, cy, size)` returns Track B's motif once `deck.motifs` provides `lion_mark`, else `None`.

### 3.2 Aces: draw everything except the indices

- **The big pip.** Use `frames.ace_pip_d(suit)`: the A♠ at **u 306.56** with its top at y 140 and its plinth ending at y 514 (D1: same 374 px height as the brief's u 340), and the others at u 280 centred on (375, 470).
- **A♥, A♣, A♦:**
  - **Keyline.** `frames.ace_keyline_d(suit)` gives the closed centreline 10 px outside the silhouette. Stroke it FINE gold with `stroke-linejoin="miter"` and `stroke-miterlimit="10"`.
  - **Caption** in gold Barlow Condensed SemiBold: `frames.ACE_CAPTION` (line 1 cap 16, +220, baseline 760; line 2 cap 12, +200, baseline 790) and the verbatim copy in `frames.ACE_CAPTION_TEXT`. The brief gives these settings only for the A♥ (§H.14); A♣ and A♦ reuse them.
- **A♠** has **no keyline and no 760/790 caption.** Its gold is inside the silhouette (the emblem) plus the waterline and bubble columns outside, and its four-line **legend** is `frames.ACE_SPADE_LEGEND` (§H.13):

  | # | Text | Setting | Baseline |
  |---|---|---|---|
  | 1 | HEADWATERS | Roboto Slab 700, cap 30, +120 (`frames.slab_line`) | 590 |
  | 2 | PLAYING CARDS OF THE SAN MARCOS SPRINGS, between drawn em-rules | Barlow, cap 12, +200 | 625 |
  | 3 | NEVER KNOWN TO CEASE, between FINE em-rules | Barlow, cap 14, +250 | 660 |
  | 4 | NAMED FOR ST. MARK · MDCLXXXIX | Barlow, cap 13, +220 | on a **sagging** arc (concave up), R 600, lowest point y 735 |

  The §H.13 geometry table, re-derived for the D1 spade, is `frames.ACE_SPADE_GEOMETRY`: apex y 140; width 107 at y 200 (x 321.5–428.5) and 217 at y 262; widest y 342.3, 306.6 wide (x 221.8–528.3); lobe bottoms y 422; stem/lobe crotches (sharp) y 397.5; stem 32.8 wide at y 400 and 60.2 at y 480; plinth y 483.3–514 (upper tread 92 wide to y 498.6, lower 122.6). At y 350 the silhouette spans x 221.9–528.1, so the waterline dashes (15–55 px beyond it) run x 167–207 and 543–583. The lion (head (375, 262), mane r 60) clears the straight sides by ≈ 21 px.
- **Interior lines are geometric knockouts.** Lines "knocked out to paper" inside a pip are holes in the pip's fill path (see §5).
- Keep art ≥ 12 px from the index (QA 10c warns).

### 3.3 Jokers: draw everything except the vertical JOKER index

- The figure sits in y 162–712 (`frames.JOKER_FIGURE_Y`; §F.4's 90–640 lowered by `JOKER_DY` = 72, see §10). Above y 310 it keeps x ≥ 130, clear of the stacked index (`frames.JOKER_*`). QA check 10c fails any figure ink at x < 130, y < 310 (or in its 180° copy) and any art within 12 px of the JOKER letters.
- `frames.joker_rule_fragments(color)` draws the FINE rule, 360 px long at y 762 (`frames.JOKER_RULE_Y`), with Ø6.3 terminals.
- The title is Roboto Slab 700 at cap 28 and +200 tracking, on baseline 817: `frames.slab_line(text, 28, F.JOKER_TITLE["baseline"], 200)`.
- The subline is Barlow at cap 12 and +200 tracking, on baseline 857: `frames.type_line(...)`, flanked by `frames.em_rules_d(bbox, 12)`.
- Watch the layer trap (§2.1): the Little Joker's gold and jade inside its Aquifer body must be cut out of the body.

### 3.4 Back: draw everything

- The system paints only the Limestone stock, which forms the white border.
- You draw the **jade flood**: inset 37.5, corner radius 18, with every line **reversed out geometrically**. The flood is one FILL path with holes (see §5), on the `jade` layer.
- There are no indices and no text.
- QA check 11: the frame is D2 and the emblem C2 — no asymmetry cluster ≥ 4 px² after a 1 px erosion, so even one missing Ø 4.2 bubble fails — the emblem is not mirror-symmetric, and knockout coverage is 18–22 %.
- The lens double rule of §H.19 (FINE lines 6 px apart, centre to centre) leaves 3.9 px of jade between the two reversed-out lines: legal (solid bridges ≥ 3), but it is the tightest spot on the frame; keep the tips from pinching.

## 4. Strokes (§B.2): the only legal widths

| Token | px | Use |
|---|---|---|
| `T.HAIRLINE` | 1.6 | awns, caption em-rules, dashed spandrel contours; never a contour |
| `T.FINE` | 2.1 | the monoline: ornament, **all hatching**, gold rules, band rules |
| `T.MEDIUM` | 3.1 | court interior detail, joker contours, partition line, knockout lines in solid pips |
| `T.RULE` | 4.2 | court frame, outer rules, court upper eyelids |
| `T.CONTOUR` | 6.25 | court figure and major attribute silhouettes |

**Caps and joins**

| Element | Caps | Joins |
|---|---|---|
| Ornament and figure strokes | round | round |
| Hatch lines | butt, ending on the contour's centreline | — |
| Frames, rules, fault-steps, lozenges, ashlar | butt | miter, miterlimit 4 |
| Vesicas, spikelets, stalactites, compass points | — | miter, miterlimit 10 |

**Hatching** is FINE at a 7.0 px pitch in exactly one half of a split shape. There is no cross-hatching.

**Dots** are Ø4.2, 6.3 or 8.4, and free line ends take Ø6.3 terminals.

**Author at final size.** A `transform` — the attribute *or* a CSS `transform` in `style` — may only be a translate, a rotate or a ±1 mirror; never scale a stroke.

**Banned in the SVG** (QA checks 1, 4 and 17 fail them): `<text>`, `<use>`, `<symbol>`, a nested `<svg>` (its viewBox can scale), `<marker>`, `<switch>`, `<image>`, `<a>`, `<style>`, filters, gradients, masks, patterns, `vector-effect`, opacity < 1 and blend modes. To reuse a shape, transform its **path data** — `G.transform(d, M)`, `G.rotate(d, …)`, `G.translate(d, …)`, `G.mirror_x(d, …)`, or `Frag.place(x, y, rot)` / `Frag.rotate(…)` / `Frag.rot180()` in Track B — so every stroke is baked at final size. (The brief's "build each once as a `<symbol>`/path" is honoured by building once in Python and emitting paths.) Set all type as outlines with `inkkit.typeset.text_to_path`, or use the `frames.type_line` and `frames.slab_line` helpers.

## 5. Knockouts, interlace and spacing are GEOMETRY

Anything "knocked out to paper" or "reversed out" is a **hole in the solid**. Never paint a paper-coloured shape on top.

```python
from inkkit import geom as G
lines = G.outline(line_d, T.MEDIUM, cap="round", join="round")   # stroke -> FILL
pip   = G.difference(frames.ace_pip_d("H"), lines)                # holes = paper
# or with Track B:  M.knockout(solid_d, frag)  /  M.reversed_out(solid_d, frag, color=T.JADE)
```

- **Interlace crossings (§B.2).** Cut the under-stroke with a 4.2 px gap on each side of the over-stroke. Use `inkkit.geom.knockout(under, over_outline, gap=4.2, lines=True, lw=w)`, or Track B's `M.interlace(under, over)` or `M.cut(frag, obstacle)`. Never use a paper halo.
- **Gold on red** is allowed only as a solid shape with an Aquifer contour. Never draw thin gold lines on red (§C.4). QA check 5r warns about gold features ≤ 4 px wide sitting on red.
- **The layer trap** (§2.1): a lower plate inside a higher solid must be cut out of the solid.

### 5.1 Minimum spacing (§I.12) — what QA check 12 measures

**Vector (fails ✗).** Every drawn element is outlined with its true width, caps and joins, with clips and transforms applied, and split into connected pieces (sub-paths count separately). The paper between any two pieces, **across all layers**, must be:

| Between | Minimum |
|---|---|
| two strokes running alongside each other for ≥ 12 px | **4.2** (parallel strokes) |
| two strokes that only approach (ends, tips, bubbles) | **3.0** |
| pieces on different layers (e.g. a gold bead and an Aquifer ring) | **3.0** (registration) |
| two fill pieces of one layer — i.e. a knockout line or a gap in a solid | **2.5** (BACK: 1.6, since all its lines are reversed-out §B.2 FINE/HAIRLINE art) |
| solid bridges between knockout holes, or a hole and the edge, in solids ≥ 300 px² | **3.0** |

Touching or overlapping pieces (joins, fills under contours, hatch butting a contour) are fine. Exempt: the frame RULE ↔ gold rule pair (§F.1's 7 px leaves 3.85, `frames.RESOLUTIONS["frame_gap"]`) and clipped art ↔ frame rules (the art window is the frame's design). Each finding lists the gap, the rule and its position, and is marked red in `build/qa/flags/<stem>.png`.

**Raster (warns !).** Per layer at 3×: features thinner than 1.5 px (below HAIRLINE — e.g. a hairline fill) and paper narrower than 2.5 px inside one layer (notches, tiny holes). Confirm each by eye.

## 6. Helpers you can import

| Module | What |
|---|---|
| `deck.tokens as T` | palette, stroke tokens, fonts, index and frame numbers (read-only; never edit it) |
| `deck.pips as P` | `pip_d(suit, u, cx, cy, rotate=False)` (bbox-centred FILL), `pip_top_d(suit, u, cx, top)`, `pip_bbox`, `pip_size`, `optical_u` (hearts ×1.04), `SPADE_H` (1.22), `ACE_SPADE_U` (306.56) |
| `deck.frames as F` | `art_window_d()`, `court_clip_d(rank, cut_y)`, `corner_pip_d(suit)`, `medallion_radius(rank)`, `CORNER_PIP_CLEAR`, `GAP_PARALLEL`/`GAP_MARK`; `house_mark_fragments(suit, cx, cy, color, compact=False)`; `lion_mark_fragments(cx, cy, size)` (Track B hook); `ace_pip_d`, `ace_keyline_d`, `ACE_*` incl. `ACE_SPADE_LEGEND`, `ACE_SPADE_GEOMETRY`, `ACE_CAPTION`, `ACE_CAPTION_TEXT`; `JOKER_*`, `joker_rule_fragments`; type: `type_line(text, cap, baseline, tracking)` (Barlow), `slab_line(...)` (Roboto Slab 700), `em_rules_d(bbox, cap)`, `cap_to_size(font, cap)`; `RESOLUTIONS` (every resolved ambiguity) |
| `deck.index as IX` | `INDEX_BLOCK_BOTTOM` (239.6 with the D1 spade); `rank_d`, `index_pip_d` — the index geometry aces and jokers keep clear of |
| `deck.cardsvg as C` | `layers_merge(...)`, `rot180(fragment)`, `two_headed(layers, clip_d)` (the system calls this for courts) |
| `deck.motifs as M` | **Track B** (`from deck import motifs as M`). A `Frag` model with `.layers()`, `.outline()`, `.shape()`, `.place()`, `.rotate()`, `.rot180()`, `.mirror_x()`; builders such as `stroke`, `fill`, `dot`, `terminal`, `ring`, `hatch`, `half_hatch`, `knockout`, `reversed_out`, `cut`, `interlace`, `clip`, `c2`, `cn`, `d2`, `bilateral`, `bubble`, `bubble_row`, `bubble_triad`, `vesica_d`, `lozenge_d`, `arc_d`; motif builders (Source Rosette, running wave, reed ladder / node / medallion, lens cartouche and field, vent roundel, fault-step and plinth, strata, karst voids, stalactite, drip fringe, scale lattice, cypress knee / cone, comb spray, ashlar, arcade, rowel star, stepping stones, festoon, pearl beading, conduit, volute, tooled scroll…). See `deck/motifs/README.md` for the current API. |
| `inkkit.geom as G` | exact booleans on d-strings (`union`, `difference`, `intersection`), `offset`, `outline` (stroke → fill), `clip` and `clip_out` (for stroke art), `knockout`, `transform`, `rotate180`, `mirror_x`, `Curve`… |
| `inkkit.typeset` | `text_to_path(font, text, size, x, y, anchor=, tracking=)` |

**Do not use** inkkit's engraving features in the deck: `stroke.py` tapered strokes, `hatch.engrave`, `tonal`, `stipple` or `dot_screen`, guilloche, or filigree or acanthus scrolls. The brief bans them.

## 7. Build, preview, QA (run from the project root)

```sh
.venv/bin/python -m deck.build KS              # -> cards/KS.svg, build/png/KS.png (750 w), build/png/small/KS.png (188 w)
.venv/bin/python -m deck.build KS --stock white   # QA variant on white -> build/white/png/KS.png
.venv/bin/python -m deck.qa KS                 # rebuilds KS on both stocks, then its checklist row;
                                               # details in build/qa/report.json, flags in build/qa/flags/KS.png
.venv/bin/python -m deck.build all             # whole deck (< 60 s) + build/contact.png
.venv/bin/python -m deck.qa all                # whole deck (< 2 min) + build/white/contact.png
.venv/bin/python -m deck.build all --print     # + §B.1 print files, 825 x 1125 with 37.5 px paper bleed -> build/print/
```

- The IDs accept file stems (`JOKER-RED`) and groups (`numbers courts aces jokers back all`).
- `deck.qa` always rebuilds the pieces it checks, so its rows describe your current `art/<ID>.py`.
- Look at every render with a viewer, and crop with `magick build/png/KS.png -crop 400x400+175+60 +repage /tmp/crop.png`.
- Check both widths, 750 and 188 px, on both stocks, Limestone and white.

**Before handing in a piece**, `deck.qa <ID>` should show ✓ for checks 1, 4, 4b, 5, 6, 8, 10a, 10c, 12, 17, 24 and 25. Treat `!` (4c hidden art, 5r gold on red, raster part of 12) as prompts to look at `build/qa/flags/<stem>.png`, and confirm each one by eye. Then run through the brief's human checks: §I.2–3, 7, 13–16 and 18–23.

## 8. Skeleton

```python
"""art/KS.py: K♠ The King Beneath (brief §H.1)."""
from deck import tokens as T, frames as F
from deck.cardsvg import layers_merge
from inkkit import geom as G, svg as S
# from deck import motifs as M        # Track B: Frags -> frag.layers()

# CUT_Y = 525   # only if an attribute must visibly cross the band

def build():
    robe = G.rect_d(190, 330, 370, 200)          # top half only; runs past 511, the system clips it
    fills = {"jade": [S.path(robe, fill=T.JADE)]}
    lines = {"ink": [S.path(robe, fill="none", stroke=T.INK, stroke_width=T.CONTOUR,
                            stroke_linejoin="round")]}
    return layers_merge(fills, lines)             # (or: layers_merge(frag.layers(), ...))
```

## 9. Resolved ambiguities (full text in `frames.RESOLUTIONS`)

- **Band cut:** art is clipped at the band's top rule (y 511) unless the module sets `CUT_Y = 525`.
- **Frame gap:** §F.1's 7 px (centre to centre) between the RULE frame and the gold rule leaves 3.85 px of paper; kept as a brief-mandated exception to §I.12 (widening it would squeeze the art window against the gold rule).
- **King rings:** "6 px apart" is read so that §I.12 holds: 6.3 px centre to centre (r 28 / 21.7), 4.2 px of paper.
- **Queen medallion:** the Ø 44 ring is the medallion's edge (Ø 46.1 overall, below the King's 58.1, so the rank grade reads by size); the 8 beads sit inside it (r 15.85, at 22.5° + 45° k), 3 px from the ring, and the house mark is the compact version (≈ 20 px). Queen ♥ mark: a linked chain of bubble rings Ø 5.6 / 10 / 5.6, tangent on the diagonal (spaced rings cannot fit inside the beads with 3 px gaps; dots would read as stray beads). The ♣ mark's leaf blades spring from the knot's top and bottom.
- **♠ fault-step:** the two lines are exact parallel offsets of one stepped centreline (risers at x 378.65 / 371.35), so the paper is 4.2 everywhere, and they are 7.3 apart (MEDIUM lines 6 apart leave 2.9). Step: D4.
- **Partition line ends:** x 143–607, ≈ 7 px clear of the gold rules; the ripple spans 5.25 wavelengths each side (x 144–606) and ends level, on a trough (left) and a crest (right).
- **♣ reed:** leaf pairs every 48 px at 375 + 48k; on node positions (every 96) the blades spring from the node's ends, so node + blades repeats the house mark along the stalk. Band nodes are solid Aquifer knots; the gold house-mark node is an outline (§C.1 restricts flat gold fills).
- **♦ ford:** 12 × 10 stones with their tips on the rules (a 10 px stone cannot float in the 6.9 px channel).
- **Corner pips:** all four suits top-aligned at y 62 and centred on x 190; the ♠ runs to y 169.4 with D1.
- **Ace layer order:** A♠/A♣ use paper, jade, red, ink, gold (§K); A♥/A♦ already have gold above red.
- **Knockout-line minimum on the BACK:** §I.12's 2.5 px applies to knockout lines inside solid shapes (pips, panels); the back's reversed-out linework is itself the §B.2 FINE/HAIRLINE art (§H.19), so QA uses 1.6 there.
- **White stock:** `--stock white` writes to `build/white/`, so the Limestone print files in `cards/` are never overwritten.

## 10. Deviations from brief

Each is the smallest change that fixes a legibility or quality problem the brief's literal numbers cause. The rest of the brief stands.

- **Joker layout lowered 72 px (client correction, 2026-09-24).** §F.4's figure band (y 90–640), rule (690), title (745) and subline (785) left each joker's composition ~75 px above the card centre. All four are lowered by `frames.JOKER_DY` = 72 so the block is optically centred; the index clearance zone (x < 130, y < 310) is unchanged.

| # | Brief | Built | Why |
|---|---|---|---|
| **D1** | §E.1 spade: "heart flipped, **scaled to 0.80 u tall**", 1.00 × 1.10 u; §H.13 A♠ u 340 | The heart construction flipped **at full size**: circle lobes (r 0.26 u at ±0.24 u), straight tangents, apex 83°; stem 0.07 → 0.20 u over the same 0.20 u below the lobes; spade **1.00 × 1.22 u**. Index spade 62 × 75.6 (block ends y 239.6, brief ≈ 234); field 116 × 141.5; corner pip 88 × 107.4 (to y 169.4); **A♠ u 306.56** so it keeps its 374 px height, top 140 and plinth bottom 514 (41 % of the card width, brief 45 %); §H.13 table re-derived (§3.2). | The squash turns the lobes into 0.87 ellipses (not circles, against §E.1's "circles only") and blunts the apex to 91°: a squat "house-roof" spade, visibly cruder than both references (Monarchs 1 : 1.24, Drifters 1 : 1.30, apexes ≈ 65–75°), worst on the A♠ showpiece. Dropping the squash is the smallest fix and makes the spade body literally the heart pip flipped. (A longer-pointed variant, heart point at 1.00 u, 1.00 × 1.28 u, apex 75°, is on file if the director wants it closer still to the Monarchs spade.) |
| **D2** | §E.1 plinth: upper step 0.26 × 0.05 u, lower 0.36 × 0.05 u | Upper **0.30** × 0.05 u, lower **0.40** × 0.05 u: two equal 0.05 u treads over the 0.20 u stem foot. | The brief's upper tread overhangs the stem by 0.03 u (1.9 px at index size, 0.5 px at 25 %), so "the deck's one signature pip detail" reads as a slab with a nick. Equal treads (3.1 px at index, 5.8 px in the field) read as two steps at every size. Spade and club. |
| **D3** | §D.1 "Q keeps its native tail … No glyph surgery." | The Q keeps its own bowl (its upper half mirrored about the counter's centre line, closing like the O) and takes a **diagonal tail** (`index.Q_TAIL`): 14.5 px thick, leaving the bowl at 4–5 o'clock at ≈ 62° and ending square-cut at y ≈ 152.9, x ≈ 115 (corners rounded 1.6 px like Barlow's terminals). The bowl, not the ink box, is centred on x 84. No other glyph changes. | Barlow Condensed's Q tail is a vertical stub on the index axis ending 7.7 px above the pip (every other rank has 22 px). At 25 % the gap is 1.9 px; the tail fuses with the pip and the Q reads as a "0" or keyhole on a stalk — the weakest rank at a glance (§I.7). Barlow has no alternate Q. The diagonal tail reads unmistakably as Q at 188 px and clears the pip by 11 px. |
| **D4** | §F.1 ♠ fault-step: left pair y 520/526, right pair 524/530 (a **4 px** step) | Step **7.1 px = one course**: left pair y 517.8/525.1, right pair 524.9/532.2 (lines 7.3 apart, see §9), risers offset so the paper is 4.2 px throughout. 7.1 is the largest step that keeps 4.2 px to the band rules. | On K♠/Q♠ the medallion hides the riser, and with a 4 px step the two halves of the double line visibly fail to line up across the medallion — it reads as a registration error on the most-seen horizontal of the ♠ courts. With a one-course step the middle line runs straight through y 525 and the strata read as displaced by one course (G.11's fault jog "shifts the courses one course-height"; G.10 asks for a step several strokes tall), with the medallion pinned on the fault. On J♠ the step reads as a clear Z instead of a 4 px nick. |

**Brief errata (no geometry change).** §E.2's "verified clearances" hold for ♠ only. With §E.1's 1.04 u heart and club, the L-column ♥/♣ field pips clear the "10" index by 32.7 px (brief ≥ 35) and the 10's centre pips clear the side columns by 32.4 px (brief ≥ 37); ♦ gives 46.6 / 60.2. The layouts match §E.2 exactly; `deck.qa` prints the built clearances on every run so any later change to the pip silhouettes shows up.

**Considered, not changed.** The diamond's lighter ink (≈ 30 % less than the other pips at the same u) and the heart's high visual centre on 3♥/5♥/9♥ (its centroid sits 11.5 px above its bbox centre) are both traditional and within the brief; either is a one-constant change if the director wants it (`pips.SUIT_SIZE["D"]` width 0.85 u; centroid placement in `layout.py`).
