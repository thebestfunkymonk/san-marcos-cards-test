# seal job — progress log

## 1. Start (fresh attempt, no prior log)
- Read brief §H.20, §B, §C, §G, §I, §J; ART_CONTRACT; draft files. deck.build/deck.qa do not cover the seal:
  the seal builds with `.venv/bin/python tuck/build_seal.py` and carries its own QA (seal-qa.json).
- Wrote build/review/seal-critique.md. Refs: FWS photos in scratchpad (sal_contact.jpg).
- Next: rewrite tuck/_seal_salamander.py (clean C, shovel head, half-hatched trunk = costal grooves),
  add proper foil QA to build_seal.py.

## 2. Salamander rebuilt (v1-v7 in scratchpad)
- _seal_salamander.py rewritten: clean ~300 deg C (kappa table), convex broad shovel head (cheeks 1.26x trunk),
  rounded-square spatulate snout, eyes Ø4.2 at s≈21, 4.2 clear.
- Split line (dorsal line) nape -> tail, easing from the spine to the tail core's outer edge (fin base) over
  split_shift; outer half hatched: 12 costal grooves square to the spine on the trunk, fin membrane hatch at 40° on the tail.
- Limbs now SOLID slim shapes (limb_mode 'solid', half-width 2.7->2.1, filleted into the contour): reads spindly.
- Gills: solid plume (tooth 2.4 / pitch 3.3 / lean 2.6) softened with a 0.45 px open/close.
- scaled(spec, k, kw) helper; SAL_FACING -25 (head at the top, C opening at 1 o'clock).
- Next: bake the tuned SPEC (currently applied as overrides in scratchpad/seal/pv.py v7), 12 grooves exactly,
  gill fringe tuning, then foil QA (gaps) in build_seal.py.

## 3. build_seal.py rewritten with real foil QA (v8-v10)
- Plates now board, emboss, foil, dieline (tuck convention); QA row 1/4/8/12/17/25/copy -> build/tuck/SEAL-qa/.
  12 uses tuck.build_tuck.foil_gaps (foil as stamped) + tight_board + raster thin-foil. Removed the draft's
  stray files from build/tuck/qa/.
- Forelimbs moved back to s 82 (were colliding with the inner gills -> a foil pinhole), hind limbs s 178,
  12 costal grooves exactly. SPEC baked (no overrides needed).
- Tried a spring vent (ripple rings) inside the C: reads as a target/coin -> rejected (vent() kept unused in _seal_ring).
- Remaining warns: type counters/apertures in Barlow at cap 16 (intrinsic), gill-root tight board.
- Next: 8x inspection of head/hips/tail, fix artefacts, then final build + mock.

## 4. Detail pass (v11 -> final candidate)
- Snout: cap 5.5 px superellipse onto a gently widening profile (no corner kink); blunt rounded-square spoon.
- Tail tip rounding 1.2 (crisp point, was a club). Eyes moved to the front third (s 17.5).
- Removed dead code (frond gills, stroke limbs, vent). Docstrings updated.
- deck.build / deck.qa do not know SEAL ("unknown piece"); the seal's build+QA is tuck/build_seal.py.
- QA: 1 ✓ 4 ✓ 8 ✓ 12 ✓ (6 raster tight-board warns: gill-root V crotches + Barlow letter apertures) 17 ✓ 25 ✓ copy ✓.
- Next: final fresh-eyes look at mock / 3x / 1x; tuck presentation compatibility checked (_tuck_mock._seal_parts reads it).

## 5. Final (done)
- Fin hatch set to 45° (§B.2 blades); fin hatch stops 6 px short of the split line's end cap.
- Final build: `.venv/bin/python tuck/build_seal.py` -> all hard checks ✓, 6 raster tight-board warns (looked at: V crotches).
- Outputs: tuck/SEAL.svg, build/tuck/SEAL.png, SEAL@3x.png, SEAL-83.png, SEAL-print.png, SEAL-mock.png,
  SEAL-mock-small.png, build/tuck/SEAL-qa/ (json, flags, 5x crops).
- Not mine / follow-up: TUCK-PRESENTATION.png (tuck owner) embeds the seal and needs a re-render to show the new art.
