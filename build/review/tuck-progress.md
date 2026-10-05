# tuck progress log (job key: tuck)

## 0. Start (retry-safe notes)
- No progress file existed. Found from the interrupted artist: tuck/_tuck_common.py, tuck/_tuck_front.py,
  tuck/_tuck_lion.py (andante lion redraw). Dev renders in build/tuck/dev/ (front-print-1x.png = latest state).
- deck.build / deck.qa have NO tuck IDs: tuck gets its own build + QA in tuck/build_tuck.py
  (reusing deck.qa.card_geometry / vector_gaps on the foil plate).
- Seal files (build_seal.py, _seal_*.py, SEAL.svg) belong to another finisher: read-only for me.
- Plan: build_tuck.py (entry) -> front refine, _tuck_back.py (from art/BACK.py), _tuck_panels.py (sides, flaps),
  _tuck_flat.py (dieline), _tuck_mock.py (mock-ups + presentation), QA.

## 1. Pipeline built (all deliverables exist in draft)
- NEW tuck/build_tuck.py (entry: `.venv/bin/python -m tuck.build_tuck`): writes tuck/TUCK-{FRONT,BACK,SIDE-A,SIDE-B,TOP,BOTTOM,FLAT}.svg,
  renders build/tuck/TUCK-*.png (+ mocks, presentation), runs tuck QA (deck.qa geometry on the foil plate) -> build/tuck/qa/TUCK-qa.json.
- NEW tuck/_tuck_back.py (derived from art/BACK.py at build time; foil = exact union like the card's knockout; outer ladders).
- NEW tuck/_tuck_panels.py (sides A/B, top end w/ 40px diving pig + ring + droplets, bottom end ghost gambusia).
- NEW tuck/_tuck_flat.py (standard reverse-tuck dieline, placement, HOLD note non-printing magenta).
- NEW tuck/_tuck_mock.py (gradient foil + emboss relief mocks; 3/4 presentation box w/ seal from tuck/SEAL.svg + AS/BACK cards).
- Wordmark: inline = groove on upper-left edges, BORDER 3.0 / GROOVE 3.0 (legal §I.12), shadow extrusion (+7,+7) hatch,
  per-letter shadow kept 4.2 clear of other letters; glyphs+shadow centred as a unit.
## 2. Lion redraw (tuck/_tuck_lion.py rewritten; old copy in scratchpad only)
- Head: new profile table (heavy brow, long bridge, blunt nose, deep muzzle, pupil dot touching upper lid).
- Mane: 3 rows of pointed flame tufts (forms.tuft_row, bow 0.1, skew 0.8) -> reads as lion mane (curls read as poodle).
- Wing: raised, root at withers behind mane, coverts along arm, 5 primaries up/back + 3 secondaries over back.
- T-junction overlap helper `behind()` (occlude by region shrunk 0.5px) to kill hair-gaps.
- NEXT: flank modelling, tail placement, mouth corner, QA gaps (front/panels), frame/lintel clearance, mocks review.

## 3. QA model + cleanup tools (cycle 2-3)
- build_tuck QA 12 now measures the FOIL AS STAMPED (exact union): separate pieces >= 3.0, parallel (local patch run >= 12) >= 4.2,
  enclosed board >= 2.5 (type counters = warn, brief-mandated micro sizes), foil >= 1.6; + wordmark solid bridges via deck vector_gaps;
  raster tight-board clusters = warn. (Deck's per-element pairwise check false-flags every 3-stroke junction in line art.)
- _tuck_common: heal() (extend/trim stroke ends), enforce_gaps(), plug() (trap fill < 2.5 wide, <= 25 px², never type counters),
  prune_parallel() (drop hugging runs of back lines), type_hull().
- Lion: shingled feathers + prune; S-tail rising w/ tuft_row tuft round the terminal; paws open onto ledge; ear clearing;
  hatch min_len 10 (no corner stubs); FIG_DY=12 (figure lower in lens); lens inner rule 6.6 (4.4 clear).
- Wreath: spikelets stamped solid (foil can't hold 2 px counters); knot removed (ribbon ties the wreath).
- FRONT vector QA: 0 hard findings (as of this entry). NEXT: full build, look at front/back/panels/mocks, fix panels QA.

## 4. Box structure + panels + lion polish (cycles 3-4)
- Flat restructured: lid (top end + tuck flap) hinged on the FRONT (front stays whole); flap tucks behind the BACK,
  whose top edge carries the thumb notch (K.NOTCH_R 70) — tuck back cuts art 9px clear + FINE arch; top plinth removed there.
  Bottom end hinged on the back (rotated 180 in flat). Seal (presentation) laid across the back's top edge.
- Back foil = exact union + plug; side B columns tightened (pitch 30/sep 14); pig tail/eye/droplets and fish rays spaced.
- Wordmark: groove zone = exact round erosion (bridges >= 3), close grooves joined, groove fragments filtered.
- Lion: head shifted right (EYE -97), straight lip + slanted jaw, bigger forepaw w/ 4 toes, S-tail tucked in lens with
  brush tuft + outward hook + terminal (tuft_row version read as a snake head -> replaced).
- _tuck_mock.py was corrupted once by a bad str.replace (empty match) and REWRITTEN in full — if a retry sees odd size, check it.
- QA status before this entry: all panels 12 ✓; FRONT 12 ✓ after tear-line fix; SIDE-B render diff fixed by 3x check.
- NEXT: full build + look; side-B HOLD note placement (outside frame); wordmark vs posts; final log + report.

## 5. Final (cycle 5)
- Lintel posts: ladder rungs/nodes near the lintel are dropped whole (no half nodes); HOLD note moved to side B's outer margin.
- Raster tight-board warnings now exclude type (groove/counters are knockouts by design); remaining = V-junction wedges.
- Final `.venv/bin/python -m tuck.build_tuck`: all hard checks ✓ on FRONT/BACK/SIDE-A/SIDE-B/TOP/BOTTOM/FLAT; copy §J.2 ✓.
- Outputs: tuck/TUCK-{FRONT,BACK,SIDE-A,SIDE-B,TOP,BOTTOM,FLAT}.svg; build/tuck/TUCK-*.png (+ -mock, PRESENTATION, FLAT, SIDES, ENDS).
- Open weaknesses: lion flank sparse; tail tuft small; type counters (A at cap 14 = 2.03 px) flagged for printer proof;
  dieline is generic (replace); acknowledgment on HOLD.
