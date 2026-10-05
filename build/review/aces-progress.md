# aces progress log (job: aces)

## 0. Baseline (start)
- No previous progress file; fresh start. Baseline renders in scratchpad v0.
- deck.qa aces baseline: AS ✗ check 12 (0.29 px < 3 strokes art/art at [434.7,334.9] & mirror, [454.8,351], [300,372.8]...); AC ! raster 12 (gold thin/narrow gaps); AH, AD pass.
- Next: write critique (build/review/aces-critique.md), then fix AS gaps, rework AC spray + wreath.

## 1. Critique written
- build/review/aces-critique.md (A♣ rework spray + wreath; A♠ QA12 near-misses + wings + face; A♥ rosette; A♦ polish).
- Scratch: /tmp/claude-1000/-home-luke-Projects-design/55d08c26-3490-4d22-8bb1-5d547fef47ba/scratchpad/fin (look.py helper renders preview + crops).
- Next: A♣ spray rework (drafting in scratch, then art/AC.py + art/_aces_reed.py).

## 2. A♣ exploration (scratch fin/spray.py, v3–v19)
- Tried fountain / lyre / tall-lyre / weeping / tassel / descend layouts. Chosen: TALL LYRE — two §G.4 ribbon
  leaves (lit half solid paper, shaded half = edge line + perpendicular bars, W 15) rise from the stem base
  flanking the culm, tips curling out in the top lobe; female brush (terminal + 2 pairs, pedicel 8 @50°, lean 18°,
  awn 12) at the top; male branches spring from the culm, pass BEHIND the leaves and DESCEND into the side
  lobes with florets hanging straight down ("descend" variant, v14) — least face-like at 188.
- Wreath: library deck.motifs.rice.rice_wreath_arc (continuous stem, pairs every 14°, 6 % shrink, knot),
  r 190, leaf_len 58, ratio 11, angle 20, inner_scale .6, inner_angle 34, tip=None + own rice_stalk spike
  (pedicel 8, spread 64, pitch 14, awn 15) -> zero QA-12 gaps in isolation (fin/wr.py wreath2).
- Next: write into art/_aces_reed.py + art/AC.py, full-card QA.

## 3. A♣ committed to art/ (cycle 1–3)
- art/_aces_reed.py rewritten (grain, female_panicle, male_branch, ribbon_leaf [lit+hatched, windows>=3.3],
  leaf_with_sheath, wreath [library rice_wreath_arc + own 8px-pedicel spike]); art/AC.py rewritten (tall lyre).
- Fixes found by looking: blade crossed the stem/lobe notch at (388,497) -> split ink (QA 12 fail); sheath now
  a straight line x≈382 up the waist, collar y 492 above the notch; male branch roots moved below the female
  pairs; single slanting/drooping male branch per side (arched ones read as eyes-with-lashes again).
- Vector QA 12 clean; remaining: gold RASTER warnings in the wreath (narrow tip hatch). Next: look at flags, then A♠.

## 4. A♠ wings (cycle 4)
- art/_as_lion.py: wing() replaced by a SICKLE leading edge (shoulder behind the mane -> out -> radius-22 elbow ->
  up the spade's upper edge -> curls in over the head), 3 covert rows INSIDE the sickle, 5 half-hatched flight
  feathers fanning from under the arm into the lobe. The old P1 "strap" is gone. Original saved in
  scratch fin/as/_as_lion.orig.py. Prototypes fin/as/wing2..4.py (wing4 adopted).
- QA 12 still failing (≈50 near-misses): categories = (a) hatch ends vs lines ending on the same contour from the
  other side (T-junction through a contour), (b) vent rings too close (3.68 < 4.2) and paw sole 0.9 px over ring 2,
  (c) nose/lip 0.7, brow/face 2.57, mane tiers 3.93.
- Next: face redesign (nobility), vent rings + paws, hatch-conflict pruning.

## 5. A♠ face, vent, clearance (cycles 5–7)
- Face redesigned (FACE dict): strong level brow flowing into a long nose bridge, eyes slanted 10°, wide nose pad,
  ω mouth (philtrum to 17.8), no muzzle "moustache" — reads as a noble lion. Inner mane tier tip r 36->37 (parallel 3.93 fix).
- Vent rings re-solved (42,2.4)/(62,9.5)/(80,16): >=6.45 c-c everywhere; vent clipped behind the paws' convex hulls.
- AS.emblem: lion = drop_specks(prune_hatch(...)) — prune_hatch drops hatch lines that come within 3 px of a mark
  they don't join (mirrored so it stays bilateral); plinth/conduit excluded. (A generic trim pass was tried and
  REVERTED: it shredded the covert rows.)
- Feather bases (6,15,24,33,42) and sickle curl (19, 96°) tuned: curl tip now tucks behind the mane crown (no free
  end). Vector QA 12 on AS = clean; raster gold narrow-gap warnings only.
- Next: full-card look (750/188/white) for AS, then A♥ rosette, A♦ polish.

## 6. A♥ rosette (cycle 8)
- art/AH.py rosette(): hub RING removed (free hub dot), 8 straight ribs now run IN from the crater rim (r 19.3) and
  stop at r 8.3 (iris, not wheel spokes), bubble ring = 11 OUTLINED bubbles Ø9.4 (red eyes 3.2) at r 28.9 like the
  back's bubble ring. QA 12 ✓ in preview. Original saved scratch fin/AH.orig.py.
- Next: A♦ polish, then family pass + deck.build both stocks + deck.qa aces.

## 7. Family pass + first official QA (cycle 9)
- deck.build aces (both stocks) + deck.qa aces: all hard checks ✓ (AS ! / AC ! raster gold narrow-gap only).
- Vent slit widened: rings (41,2.6)/(62,9.6)/(80,16) (slit ground 3.1; remaining raster flags = ellipse ends,
  ear/mane acute junctions, feather/vent wedges — acceptable, by eye).
- A♦ checked: no arrows; HATCH_MIN 8 tried, no visible change, reverted. A♦ unchanged.
- Next: fresh-eyes pass on A♣ details, A♠ ear/mane raster spots, final build+QA, update critique with outcomes.

## 8. Retry resumed (cycle 10) — A♠ QA-12 regression fixed
- Found AS failing vector QA 12 (2.45 px covert/covert at (443,273) + mirror): inner covert rows were built as raw
  normal offsets of the sickle, and at the elbow (R 22) / curl (R 19) the 16.9 / 28.1 px offsets fold back into
  swallowtail loops -> tadpole loops + near-miss ends. Fix in art/_as_lion.py wing(): each row base is now a true
  shapely inner offset, FILLETED (offset by off+14 then back by 14: WING["fillet"]=14) so rows turn the elbow on a
  radius-14 arc; drop_specks also drops tiny degenerate loops. AS.py: covert speck threshold 9 -> 16 (drops a lone
  hook by the crown). Vector QA 12 clean again.
- Next: A♣ fresh-eyes rework of female brush + male florets + wreath leaf proportions.

## 9. A♣ florets + wreath tip (cycles 11–13)
- Male florets (art/AC.py FLORET/MALE): 6 plumb, evenly spaced 10.5x3.7 florets read as comb teeth / eyelashes.
  Now 4 + terminal florets 14x4.8 (3:1, a bit under the female 16x5), hung 70–84° (≈ §G.5 ±150° off the culm
  axis), pedicels alternating 11/8 -> they dangle. Tried 2 branches/side (reads as candelabra tree) and branches
  IN FRONT of the leaves (bites out of the leaves, moustache) — rejected.
- Male branch ROOT stubs (between culm and leaf) dropped (role 'branch' < 14 px): read as an arrowhead on the culm.
- _aces_reed.wreath(): the stem was being cut 4.2 px short of its own flowering spike (6 px gap stem->spike). Now
  only leaves/hatch are cut by the spike; the stem runs on 10 px up the stalk (no 1.3 px notch at the 1st pedicel).
- Wreath leaf proportions tried 66–96 px (ratio 11–12): longer leaves overrun the tip spike and leave hatch
  crumbs; kept 58/11/20.
- Next: A♠ look at 3x after the covert fix; A♥/A♦ look; family 188 + white; build + qa.

## 10. A♦ hatch + final (cycles 14–15)
- art/AD.py HATCH_MIN 6 -> 10: the tip-most rung on each long point left a red pill by the tip; now the hatching
  stops short of the tip. (13 tried: strips the diagonal points' hatch entirely — rejected.)
- A♥ left as is (rosette at the r-40 limit; straight ribs per §H.14).
- deck.build AS/AH/AC/AD both stocks + deck.qa: all hard checks ✓; AS ! and AC ! raster gold narrow-gap only.
- aces-critique.md: appended Outcomes + Remaining weaknesses. DONE unless a reviewer asks for more.
