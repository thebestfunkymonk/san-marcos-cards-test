# BACK "The Source" — critique (fresh eyes, 2026-09-23)

Compared side by side with `research/refs/monarchs_wopc_back.jpg` and
`research/refs/drifters_dd_03.jpg` (study only; montage in the job scratchpad).
State as found: QA 11 ✗ (knockout 16.3 %), 12 ✗ (33 vector findings), all other checks ✓.

## What works
- The idea reads at 188 px: a Source hub with two rice blades and two cypress boughs
  pinwheeling round it. It is clearly C2, not a mirror, and nothing in it quotes Monarchs
  or Drifters (no snake or sword axis, no stepped or beaded corners, no piano keys, no sunburst).
- The frame vocabulary (outer RULE and companion rule, running waves flowing outward
  from the fault-step plinth, reed-ladder sides with node medallions, vent roundels) is
  crisp, restrained and exactly D2.
- The rice ribbon leaves (half-hatched lanceolate vesicas) are the best drawing on
  the card. They carry the Monarchs "one half hatched" richness in a native form.

## Problems
1. **The density is inverted.** By area, the frame and spandrels are ≈ 9.6 % of the
   flood and the emblem only ≈ 6.9 %. In the Monarchs back the cartouche is the densest
   field and the frame is a thin, quiet border. Ours reads as a busy frame around a
   sparse centre, so the eye goes to the grey spandrels first.
2. **There are voids in the emblem rhythm.** At 2 and 8 o'clock each darter floats
   alone in a pocket of about 150 × 120 px. At 11 and 5 o'clock the space between the
   rice panicle and the bough's short counter-clockwise sprays is similarly empty. The
   Monarchs leaves sit about one leaf-width apart everywhere; ours alternate between
   dense clumps (bough sprays, stacked leaves) and holes.
3. **The bough is lopsided beyond its purpose.** The clockwise sprays are long and
   feathery, but the four counter-clockwise ones are stubs, so the top tip reads as a
   one-sided fern. It should be deliberately C2, but the short side needs body.
4. **The darters are specks.** At 188 px they are grey blobs. At 3× they are
   over-detailed for FINE reversed-out line:
   - the 9-spine dorsal fan pinches to 1.4 px of jade between spines (QA slivers);
   - the eye is a solid Ø 8.4 paper disc with no pupil (the ring and dot overlap);
   - the last stitch dash crowds the fin base, leaving 1.2 px jade bridges;
   - the tail reads as a bow tie.
5. **The spandrels mix three textures.** Solid FINE corner arcs, dashed HAIRLINE echoes
   and solid HAIRLINE lens echoes meet in each corner. At 188 px the dashed band turns
   into grey moiré rather than "rings spreading across the lake".
6. **The lens cartouche edge is weak.** Its double rule sits inside a stack of parallel
   echoes and loses its role as the one crisp boundary between field and emblem.
7. **The rice panicle is thin.** Its culm climbs a long bare stretch with a few
   drooping florets, so it reads as a wisp next to the hatched leaves.
8. **Geometry faults.**
   - Acute T-junction wedges between overlapping rice leaves: 0.63 px jade at
     (164.8, 473) and (585.2, 577).
   - Tick-to-tick near-touches in the bough: 0.98 px paper necks at (367.7, 173.2)
     and (382.3, 876.8).
   - A 1.05 px bridge at (376.6, 703.3).
   - The darter slivers listed in item 4.

## Plan
- Move density into the emblem first:
  - wider and fuller rice blades that reach into the 8 and 2 o'clock pockets;
  - a stronger panicle;
  - longer counter-clockwise bough sprays that fill the 11 and 5 o'clock voids;
  - a darter redrawn for legibility (clean fan, a real pupil, a clear stitch line),
    with each darter carrying its own orbit wake so it no longer floats.
- Then settle the spandrels into one calmer texture:
  - more solid lens echoes and fewer dashes;
  - a few more inner echoes at 3 and 9 o'clock;
  - keep the corner ripple arcs.
  Tune them last to land coverage near 19–20 %.
- Fix every sliver at its source (fin geometry, stitch end, tick spacing). For the
  unavoidable acute leaf wedges, fill the sliver inside the motif (a per-motif fillet
  closing, r 1.5), so that no jade feature is thinner than 3 px.
- Make `build()` fast: jade = flood + holes under `evenodd`. This is exact and
  identical to the pathops difference (symmetric difference 0.004 px²), and saves ≈ 11 s.

---

## Result (after about 12 critique→fix cycles; final state as of 2026-09-24 00:05)

`deck.qa BACK`: all hard checks ✓. Check 11 ✓: KO 18.2 %, emblem C2 with no clusters, mirror_lr 0.213, frame D2 clean. Check 10a ✓ (diff 0.0). Check 12 is `!` (raster only): the HAIRLINE field contours rasterise at about 1.4 px at 3× in 12 small spots; the same warning was there before, and the vector check is clean (0 findings).

What changed, against the problems above:
1. **Density.** The emblem now carries about 7.4 % of the flood (frame and spandrels 10.9 %; the balance improved, but it is still not inverted Monarchs-style):
   - a denser cypress bough, drawn on a real stem, with 8 orbit sprays, 3 left sprays and 3 cones;
   - wider rice blades (L:W about 10:1).

   The spandrels gained vent-ripple corners (10 quarter arcs, all inside the field) and a mostly solid field. Inside the lens, FINE "depth contours" at 8.4 px run wherever the emblem leaves 20 px of jade.
2. **Voids.** The 11/5 o'clock void is filled by the long left sprays. The darter pockets now hold a radial bubble triad, but they are still the emptiest places on the card (see below).
3. **Bough.** It is deliberately asymmetric: long orbit sprays sweep clockwise and shorter sprays climb on the other side.
4. **Darter.** It has been redrawn:
   - a 9-spine fan whose spines leave the back at least 4 px apart;
   - a ring eye with a jade pupil;
   - a 4-dash stitch just below the midline, with 8 readable saddles above it;
   - a caudal split that ends on the rear edge.
5. **Spandrels.** Only contour 7 dashes, near the corners, so the moiré band is gone. The corners read as vent ornaments.
6. **Lens edge.** It is still the weakest boundary on the card (see below).
7. **Panicle.** It is longer, and its 3 drooping male florets now hang clear of the leaves.
8. **Every sliver is fixed at its source or by a per-motif r 0.85 fillet.** An audit confirms at least 20 px of jade between every pair of motifs.

Remaining weaknesses:
- **Coverage margin.** Coverage sits at the low end of 18–22 %. Within the brief's hard limits (HAIRLINE field, 4–7 contours, 20 px between motifs, emblem ≤ 80 % of the lens) there is little room left.
- **Darter pockets.** The darters are still small islands at 2 and 8 o'clock, and specks at 188 px, as the brief's 100 px size makes inevitable.
- **Lens edge.** The lens double rule sits inside a continuous ripple system (field outside, depth contours inside), so the cartouche edge reads softer than on Monarchs. The vesica plus rosette can also read as an eye.
- **Panicle likeness.** The panicle can still read as wheat at arm's length.
- **Tip resemblance.** The cone plus lead spray at each tip is on the axis, like the Drifters arrow placement. The cone keeps it botanical, but it should be watched.
