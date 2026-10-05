# BACK progress log (job BACK)

## 2026-09-23 22:30 — attempt 1 start
- No prior log; fresh start. Baseline (art as found): QA 11 ✗ coverage 16.3 %, 12 ✗ (0.63 px fills at
  (164.8,473)/(585.2,577) = lens-rule near inner ripples at 9/3 o'clock; darter slivers ~1.4 px round (460,365)/(290,685);
  bough/cone gaps at (367.7,173.2)/(382.3,876.8)). build() ≈ 16 s (parts 3.7 s, union 3.5 s, difference ≈ 8 s).
- Emblem uses _back_bough (not _back_spray, _back_vent — unused drafts).
- Scratch renders: $SCRATCH/back/v*.

## 22:55 — iteration 1-2 (critique written: build/review/BACK-critique.md)
- BACK.build(): jade = flood + holes under evenodd (exact, ≈11 s faster). parts(): emblem first, frame's
  inner echoes now clipped 20 px from the actual emblem marks (frame(emblem_shape=...)).
- _back_geo: c2() expands strokes to fills before rotating (a near-threshold miter at a rice-leaf tip
  broke C2 by a 10 px spike); new fillet(f, r) = per-motif closing (r 0.85) to fill acute jade wedges.
- _back_darter: deep pivot fan (9 spines ≥ 4 px apart at the back), ring eye with jade pupil,
  stitch on the midline x 31–72, caudal split ends on the rear edge.
- _back_bough: rewritten placement: 8 orbit sprays (pitch 26, rooted near their orbit), 4 left sprays
  (pitch 48, sweeping up), collision guard (4.2 px between branchlets, twig strip exempt), lead 26.
- _back_rice: culm ends at clock 339 (panicle away from twig), first leaf tip ends clock 350.
- Result: 0 vector findings, coverage 16.90 %. Next: widen rice leaves / panicle, field solid, corners.

## 23:40 — iterations 3-6 (coverage push, all vector-clean)
- Frame: FIELD solid=6 (only contour 7 dashes); CORNER = 10 FINE vent-ripple quarter arcs r 34→124 (all
  fit inside the field, no clipped ends); INNER echoes count 4, FINE (solid ornament, §B.2), 20 px from
  the emblem marks; plinth lower tread chevron-hatched 45° (V points on the tread rules, D2-safe).
- Bough: ticks 12 @ pitch 7.8 (base 0.45), 2 orbit sprays + 1 left spray end in Ø15 cypress cones
  (_spray/_fit handle cone clearance); rachis overlaps into the cone.
- Rice: widths 27/32/32 (L:W 10–10.5), panicle 160 long, male florets on 10 px pedicels.
- geo: WALL_GAP 22 → 20.5. Emblem bubbles n=6 min_r 13.5 (no new pockets found).
- v8: coverage 17.94 % (vector), 0 findings. Still need +0.1…0.5. Ideas left: culm as double line,
  field solid 7, triads with 14 px clearance, darter pocket.

## 00:10 — iterations 7-9: coverage reached (raster 18.33 %, vector 0 findings)
- Bough twig drawn as a stem (two FINE rules 6.3 apart, round ends, sprays spring from its outer rules;
  lead rachis rises from the apex). Rice culm stem option coded but OFF (culm is hidden behind leaves).
- INNER echoes: count 6, pitch 8.4, FINE, 20 px from emblem marks ("shoaling" depth contours).
- FIELD dash_reach (150, 330) (only contour 7 dashes, near the corners).
- preview QA: 11 ✓ (KO 18.33 %), 12 raster-warn only (HAIRLINE field lines at 3× AA, same as before),
  10a ✓, 25 ✓, 24 ✓. Next: 3× polish of darter / rice / cones, 188 + white checks, deck.build + deck.qa.

## 00:30 — checkpoint: deck.build BACK (both stocks) + deck.qa BACK → all hard checks ✓, KO 18.3 %,
  12 = ! (raster: HAIRLINE field contours rasterise at ~1.4 px at 3×; vector clean). build() ≈ 11 s:
  BACK.build/holes_d now GEOS-union Frag.shape()s (emblem union built incrementally in
  _back_emblem.emblem(with_shape=True), fillet seeds its shape cache), evenodd flood+holes.
- Rice panicle: 3 male florets, gap 6, m_pitch 15 (all hang above the leaves).
- Next: polish passes (darter saddles vs fin, twig foot, lens edge), maybe a little more KO margin.

## 00:50 — polish pass (darter, spacing audit)
- Darter: stitch just below the midline (y 0.8, x 36–75, 4 dashes), 8 saddles x 37–72 lean −18 (now read as
  saddles, not a crenellated back); docstring updated (ring eye with jade pupil).
- 20 px audit between motifs: panicle tip pulled in (culm end r 309), leaf-1 tip clock 348.5, tip cone
  cone_gap 20.5, bough keep +1 px margin, inner echoes clear 20.1 → every pair ≥ 20 px.
- v14: 18.24 % vector, 0 findings.

## 00:10 (09-24) — FINAL
- Inner echoes min_len 60 (stubs dropped); triads oriented radially (grow outward from the Source).
- deck.build BACK (limestone + white) + deck.qa BACK: 10 pass, 0 fail, 1 warn (12 raster HAIRLINE AA);
  KO 18.2 %, 10a diff 0.0, emblem mirror 0.213, frame D2 clean. build() ≈ 11 s, deterministic.
- Critique + result: build/review/BACK-critique.md. Unused drafts left in place: art/_back_spray.py, _back_vent.py.
