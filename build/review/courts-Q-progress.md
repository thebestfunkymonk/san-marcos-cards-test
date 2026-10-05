# courts-Q progress (Q♠ Q♣ Q♦ polish)

Tools (mine, in work/courts-q/): crop.sh <svg> cx cy half scale out · diag.py <module> [--qa] [x,y ...]
(heal log + QA-12 on the composed marks, with roles) · qapieces.py <svg> x,y (QA pieces) · cmp3.py <ID>
(marks whose QA outline != skia outline) · leafdbg.py (QC leaf packing).

## 1. Root cause of the QA-12 "strokes" failures on QC (and a deck-wide trap)
clip_out re-serialises a closed vesica ring it touches as an OPEN polyline whose ends coincide.
Render + heal (skia) cap that seam ROUND; QA (GEOS buffer of a closed LineString) makes it a RING
with a miter spike (up to 10 x w/2). So heal thinks it is clear, QA sees a spike 1-2 px from a neighbour.
Fix (QC): _qc_parts.close_rings() closes such subpaths with Z BEFORE heal; _qc_parts.compose(sc)
= sc.compose(heal_gaps=False) + close_rings + K.heal(+band rule) — QC.build() uses it.
Then leaf tips are real miters (sharp, per §B.2) so the leaf packer checks the tip spikes
(_qc_gown._spikes, tip_zone = 3 px + half width clear of seam/opening/soft). Leaf ratio 10 -> 9
(so 125-px leaves keep their half-hatch), coronet pedicel 9 -> 12.
QC: vector 12 clean, 4c clean.  NEXT: QS, QD QA fixes; then critique.

## 2. QS + QD QA fixed (drafts in work/courts-q/out/r1)
QS: silhouette pinholes (veil/head/circlet slivers -> CONTOUR dots, the 2.66 px near-miss) closed by
QS.fill_pinholes (an empty back item). Kites xs 334/347.5/361.5 -> 338.5/350.5/363 (first kite was an ink blob
at the veil edge; 4c gold). New art/_qs_finish.py: compose = compose(heal_gaps=False) + close_rings +
trap_cut (fills cut back under ink/gold solids wider than CONTOUR, keep 1.4 px trap) + heal. Fixes the plume
junction 4c. QS.build uses it.
QD: pupil_tuck -0.5 (near pupil 2.92 px from the lower lid). art/_qd_finish.py (copy) fixes the diadem 4c.
All three: vector 12 clean, 4c clean (preview QA). NEXT: fresh-eyes critique (build/review/courts-Q-critique.md).

## 3. Critique written (build/review/courts-Q-critique.md) + balance pass (drafts work/courts-q/out/r2)
QS: gown 48 wide (linings under it), plumes +4 wide, barb pitch 10.5, locks wider below veil, handle 14,
sleeves +4, karst 28x22, band h 10, kites pulled in, seam dots from y372 inset 8, drop_crumbs in finish.
  -> paper 49.9 jade 14.6 red 11.1 gold 8.7 ink 15.7
QC: BERTHA 35, pearls d_mid 10 gap 6.5, sceptre hw 9.5, coronet band h15 top162, DRIFT along40 across17,
gown shoulder x226 hem x200 -> paper 45.3 jade 15.4 red 11.0 gold 9.7 ink 18.6
QD: stomacher hw 38/33, staff_hw 9 -> paper 45.6 jade 16.1 red 12.2 gold 10.0 ink 16.1
Backups of pre-balance modules: work/courts-q/QC.before-balance.py, QD.before-balance.py.
NEXT: QS raceme, final build both stocks + deck.qa QS QC QD.

## 4. Polish pass (r3)
QS raceme 7 -> 5 florets (152, 64, -8, 5, 6.6): reads as a pendant raceme, not popcorn.
QD architrave arch_h 5 -> 8: the 0.3 px gold slit between the joint line and the CONTOUR under the
architrave (raster 12 flag [336,128,423,128]) is now a 3 px gold architrave band.
QC PACK bend (16,-16) -> (12,-12): 5 leaves per half (2 on the left). ink 18.8 (waiver 19).
Determinism checked (two processes, different hash seeds: same md5).
Official build both stocks + deck.qa QS QC QD: all hard checks pass (12 raster "!" only: kite axes,
leaf-tip wedges, HAIRLINE awn, eye corners, pediment apex). NEXT: rebuild after the QC leaf change, final QA.

## 5. DONE — final official build (both stocks) + deck.qa QS QC QD: 39 pass, 0 fail, 3 warn (12 raster only).
Balance: QS 49.9/14.6/11.1/8.7/15.7 · QC 45.3/15.2/11.0/9.7/18.8 · QD 45.4/16.1/12.2/10.1/16.2 (paper/jade/red/gold/ink).
Critique: build/review/courts-Q-critique.md (final table at the end).
