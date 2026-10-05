# SEAL — fresh-eyes critique of the interrupted draft (2026-09-23)

Draft: tuck/SEAL.svg + build/tuck/SEAL@3x.png (tuck/build_seal.py, _seal_ring.py, _seal_salamander.py).
Judged against brief §H.20 "Seal", §B.2, §C, §G, §I and the photo refs (research/refs/smtx/blind_salamander.jpg,
USFWS "Eurycea rathbuni FWS 20424-20439").

## What works (keep)
- Ring furniture is sound: 24-lobe sine ripple die (crest R165 / trough R159, non-printing magenta),
  RULE outer ring R146, FINE inner ring R115, legends Barlow SemiBold cap 16 +250 on R130, §J.2 copy verbatim.
- Legends read cleanly; bottom legend reads left-to-right; bubble strings sit at 3 and 9 o'clock.
- Single-silhouette construction for the animal (limbs unioned into the body contour) means no plain X crossings.

## What fails
1. **Not a C.** The spine turns ~395 deg (L 395 px at ~1 deg/px): the tail sweeps under the body and
   comes back inside, so the animal reads as a "?"/"G" spiral, not a single C. The centre-right of the
   field is dead red space while the mass piles up on the left and bottom.
2. **Reads as a gecko/newt, not E. rathbuni.** Head is a long rounded box barely wider than the trunk
   (hw 14.3 vs 12.4); no broad flat cheeks, no spatulate spoon snout. Trunk is a uniform tube.
3. **Gills are fir sprigs.** Tooth pitch 2.1 px / depth 1.4 px: the fringe fills in at 1:1 and at 3x
   they look like tiny pine trees stuck on the head, two of three rami per side fused.
4. **Tail fin reads as a second tail.** A long fin line 7 px inside the outer contour along the whole
   tail makes a "banana" double contour; not recognisable as a fin.
5. **Costal grooves as ticks on both flanks** read as a zipper / centipede and add lizard noise.
6. **No half-hatching anywhere.** Next to the tuck front (hatched ledge, legs, wreath) the seal is thin
   and sparse; it lacks the Jinkins density that makes foil feel engraved.
7. **Scale/balance.** The animal occupies ~60 % of the field but is visually light (outline only); the
   heavy type ring dominates.
8. **Bubble strings** start with two solid dots then rings; fine, but they could align to the text
   circle's cap band more exactly (currently OK, keep).

## Plan
- Rebuild the salamander: clean ~285 deg C centred in the field, head at 12 o'clock facing right,
  C opening at ~2-3 o'clock; broad flat shovel head (cheeks ~1.4x trunk), spatulate rounded-square snout;
  two Ø4.2 eye dots set wide in the front third.
- Dorsal midline from the neck to the tail; **outer half of the trunk half-hatched perpendicular to the
  spine at the 7.0 pitch = the 12 costal grooves** (hatch on the convex side so the pitch opens, never closes).
- Tail: compressed, with the fin shown as a crest/flange treatment that reads at 1:1 (try variants).
- Gills: 3 short solid feathery rami per side, ≈ half head width, open fringe pitch so the notches survive foil.
- Keep limbs as filleted tubes (bore ≥ 4.2), long and spindly; 4 fingers / 5 toes.
- QA: foil-as-stamped gaps (tuck.build_tuck.foil_gaps), tight-board raster, widths, structure, rsvg/resvg.

## Resolution (final, 2026-09-23)
1. C: spine turns 302 deg, no self-overlap; head at 12-1 o'clock (SAL_FACING -25), opening at 1-2 o'clock.
2. Head: convex broad shovel (cheeks 32 px vs trunk 26), blunt rounded-square spatulate snout, eyes in the front third.
3. Gills: 3 solid raked plumes a side, softened fringe, curled back; ~17 px (≈ half head width).
4. Tail fin: the split line eases from the spine to the fin base; the fin flange carries 45° hatch.
5. Costal grooves: exactly 12, as the trunk's half-hatch (outer/convex half, square to the spine).
6. Density: half-hatching band round the whole C; limbs solid and spindly.
7. QA (tuck/build_seal.py): 1 ✓ 4 ✓ 8 ✓ 12 ✓ 17 ✓ 25 ✓ copy ✓; warns: gill-root V crotches, Barlow apertures.
