# Courts Q — fresh-eyes critique (Q♠ §H.2, Q♣ §H.8, Q♦ §H.11)

Compared side by side with the approved K♠ and the finished Q♥ at 750, 1500 + 3× crops, 188 and on
white. Renders: `work/courts-q/out/cmp/` (row_top.png, row_188.png, faces.png, hands.png).
Status column: FIXED = done in this pass; OPEN = left, with the reason.

## Shared

| # | issue | status |
|---|---|---|
| S1 | QA 12 "strokes" near-misses on Q♣ came from a kit/QA disagreement: `clip_out` re-serialises a closed vesica ring as an open polyline whose ends meet; the render and heal (skia) cap that seam round, QA (GEOS) buffers it as a ring with a miter spike (up to 10 × w/2). Heal said "clear", QA saw 1.3 px. | FIXED per court: rings closed with `Z` before the heal (`_qc_parts.compose`, `_qs_finish`, `_qd_finish`); all vesica tips are now true miters (sharp, §B.2) in render, heal and QA alike. Upstream: `Scene.compose` should do this for everyone. |
| S2 | 4c: fills trapped under acute contour junctions / thin gold ends read as "lower plate under an ink solid". | FIXED: `trap_cut` cuts red/gold/jade fills back under ink/gold solids wider than CONTOUR (keeps a 1.4 px trap, no print change). |
| S3 | Hands: all six are kit fists, same construction as K♠ (mitten, 3 finger lines, separate thumb), each on a holder/shaft — never on a plant or creature. Consistent. | OK |
| S4 | Faces at 3×: the three share the kit egg, RULE lids, hook nose, two-arc bow; Q♣ and Q♦ read as sisters of Q♥; Q♠ is the deliberate outlier (closed lids + vestigial dots). One hand. | OK |

## Q♠ · The Blind Oracle

| # | issue | status |
|---|---|---|
| QS1 | QA 12: 2.66 px between two pieces of the silhouette CONTOUR over the circlet — sub-pixel slits in the veil ∪ head ∪ circlet union were stroked as CONTOUR dots (visible at 8× as ink blobs on the circlet). | FIXED: `fill_pinholes` (an empty back item closes slits < 40 px²). |
| QS2 | Circlet cramped and blotted: the first stalactite sat on the veil contour and became an ink blob (4c gold under ink); the near-end point hung off the band's end over the veil edge; the band (8 px) read as a line. | FIXED: nine points kept, xs pulled in at both ends, band 8 → 10 px. |
| QS3 | 4c red under ink at the upper/middle plume junction (a scallop notch at an acute concave corner). | FIXED by S2 (six plume variants tried first: the junction is structural). |
| QS4 | Colour: paper 50.9, jade 14.6, red 10.6, gold 8.0 — the palest court at 188 px. | IMPROVED: gown 56 → 48 px wide (lining under it: paper → red), plumes +4 px wider and barb pitch 9.5 → 10.5, locks widened below the veil, mirror handle 12 → 14, sleeves +4, karst pitch 26×20 → 28×22. Now paper 49.9, jade 14.6, red 11.1, gold 8.7. OPEN: gold stays under 10 because §H.2 makes the veil and the gown paper and gold may only fill regalia and hair; the mirror stays Ø110 (brief). |
| QS5 | Gown seam dots at the top were half-eaten by the lock/outline (read as "(" crumbs). | FIXED: the dotted seam starts at y 372 on a line 8 px inside the gown edge. |
| QS6 | A red crumb (30 px²) of lining left between the laurel's halo and the sleeve. | FIXED: `drop_crumbs` in the finish. |
| QS7 | Face at 3×: serene; the tilted head reads as listening. The vestigial dots are right under the lash lines (3 px) and read as the brief's "dots beneath the lid". The far dot sits near the cheek contour and could pass for a mole. | OPEN (minor; dot_gap is already the §I.12 minimum). |
| QS8 | The laurel raceme reads as a clump ("popcorn") at 750: 7 overlapping florets. | FIXED: 5 florets on a longer, more drooping axis; it now reads as a pendant raceme. |
| QS9 | Must-haves: salamander anatomy (flat head, two dot eyes, spindly legs, finned tail, 3 red gills a side) ✓; closed eyes with dots ✓; red gill-plume ruff ✓; not touching a hand ✓. | OK |

## Q♣ · The Wild-Rice Queen

| # | issue | status |
|---|---|---|
| QC1 | QA 12: 1.31 / 1.51 / 1.93 / 2.1 px — gown leaves' tips and a coronet spikelet (S1). | FIXED: S1 + the leaf packer now checks each leaf's two miter-tip ends against a tip zone (3 px + half width clear of the seam, the opening and soft objects); coronet pedicels 9 → 12. |
| QC2 | Once the tips are real miters, the packer kept only 125-px leaves on the right, and 125 / 10 = 12.5 px is under the 12.6 px half-hatch minimum: the textile lost its hatching. | FIXED: leaf ratio 10 → 9 (every leaf ≥ 13.9 px keeps its midrib and half-hatch). |
| QC3 | The "current-streamed leaf gown" (must-have) is thin: 4 leaves per half, 3 of them on the viewer's right; the fan and the left arm cover most of the left panel. | IMPROVED: leaf S-bend 16° → 12°, so 5 whole leaves fit per half (2 on the left). OPEN: still light at 188; with whole-leaf rules this is what the visible panel holds (tried grid, heading, gap, ratio and border variants). |
| QC4 | Colour: red 10.1, gold 9.5, ink 18.8. | IMPROVED: bertha 30 → 35 px with fewer, smaller pearls; the gown's sides moved in 4 px (more red lining shows); sparser drift knockouts; sceptre culm 17 → 19 px; coronet band 13 → 15 px. Now red 11.0, gold 9.7, jade 15.2, paper 45.3, ink 18.8 (within the 19 % waiver). |
| QC5 | Face: calm, pupils toward the sceptre (§H.8 "eyes on the sceptre"). Grace good. The egret fan is the heaviest shape on the card; its vane edges read slightly flame-like at 750. | OPEN (identity; the §H.8 fan). |
| QC6 | Must-haves: florets are correct (erect female spikelets at the tip, male florets hanging below) ✓; leaf gown ✓ (thin, QC3). | OK |

## Q♦ · The Queen of Scales

| # | issue | status |
|---|---|---|
| QD1 | QA 12: the near pupil 2.92 px from the lower lid (the kit's parabola estimate says 3.0). | FIXED: `pupil_tuck` −0.5 (the pupil hangs 0.5 px into the RULE lid). |
| QD2 | 4c gold under ink at the portico's pediment corners and the beam ends. | FIXED by S2. |
| QD3 | Colour: gold 9.5. | FIXED: stomacher 72/62 → 76/66 px, staff 16 → 18 px. Now paper 45.4, jade 16.1, red 12.2, gold 10.1, ink 16.2: every channel in band. |
| QD6 | Raster 12: a 0.3 px gold slit ran the full width of the architrave, between the joint line and the CONTOUR under it (at 1× it looked like one ink bar). | FIXED: architrave 5 → 8 px, now a visible 3 px gold band between two lines (classical). |
| QD4 | The arcade's keystoned arches read as small arched windows at 4×, bell-like at 1×. | OPEN (identity; reads as an arcade on the gown at 750). |
| QD5 | Must-haves: level scales holding water (ripple rings on jade pans) ✓; portico diadem with oculus over four column-teeth ✓; no blindfold, sword or gavel ✓; paintbrush with red-dipped bracts and jade leaves ✓. | OK |

## Legibility at 188 px

All three read at a glance as queens of their suit: Q♠ by the veil, the red ruff and the round mirror; Q♣ by the
spikelet coronet and the rice sceptre; Q♦ by the portico diadem and the scales. Q♠ is still the palest of the
five (QS4).

## Final (deck.build on both stocks + deck.qa)

| court | paper | jade | red | gold | ink | hard checks |
|---|---|---|---|---|---|---|
| Q♠ | 49.9 | 14.6 | 11.1 | 8.7 | 15.7 | all ✓ (12 raster `!`: circlet axes in narrow points, cuff wedges) |
| Q♣ | 45.3 | 15.2 | 11.0 | 9.7 | 18.8 (waiver 19) | all ✓ (12 raster `!`: leaf-tip wedges, HAIRLINE awn, fan vanes) |
| Q♦ | 45.4 | 16.1 | 12.2 | 10.1 | 16.2 | all ✓ (12 raster `!`: pediment apex, scale finial, eye corner) |

Remaining weaknesses: Q♠ gold (8.7) and red (11.1) stay under target (the brief's paper veil and gown; gold may
only fill regalia and hair; the mirror is fixed at Ø110). Q♣ red 11.0 and a light leaf textile. Q♦'s arcade glyphs
are small. The raster `!` flags are all acute-junction wedges of the kind the K♠ keeps.
