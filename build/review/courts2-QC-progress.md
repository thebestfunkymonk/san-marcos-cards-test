# courts2 — QC (Q♣ Wild-Rice Queen) progress

Owner files: art/QC.py, art/_qc_*.py. Work dir: build/review/courts2-QC/work (round-start copies of the art files there).

## Iteration 0 — inspection of the kit-rebuilt QC (750, 188, 3×/6×/10×/12×/20× crops)
Remaining problems found:
- hR (sceptre, palm view): lowest palm-view fingertip lobe ends ~0.2 px above the fist's bottom contour (hook touching the heel line) — kit-level, patch locally.
- hR: jade gown sliver with a spur/bite between the right sleeve's edge and the culm halo round node collar 488 (≈3–6 px of jade).
- hL (fan): back of hand/wrist long and parallel-sided (glove), leaf of the gown textile emerging at the cuff's corner.
- ferrule: outline broken at upper-left by heal (plume outlines 1.3–1.9 px away) → paper sliver inside the ferrule's contour.
- knop: base sits exactly on the cloak's top CONTOUR (round nubs at the corners).
- left male-arm tip floret of the sceptre tangent to the hair's outer CONTOUR (≈484–494, 248–275).
- hair parting: lock inner edges leave the crown 4.6 px apart (acute gold tent, < 4.2 px paper between strokes).
- ink wedge in the fan at (225–230, 346–354) where plume outlines meet the cloak line.
QA (preview): 12 warn (2 thin = awns, 12 narrow-gap = plume/leaf tips), balance paper 44.4 red 11.4 ink 18.6.

## Iteration 1 — fixes (art/QC.py, new art/_qc_hands.py)
- knop: knop_y 281 → 286 so it STRADDLES the cloak's top line (the silhouette meets its round sides at mid-height, like the collars at the shoulder on K♠/K♣/K♦/Q♦). Raising it (270.5) left an 8 px culm neck with CONTOUR sides and ink-filled corners: rejected.
- sceptre male arms: (62°, (18,50)(32,60)(12,30), florets .35/.61) → (66°, (18,50)(30,62)(10,36), .33/.60): tip floret 3.2 → 9.4 px off the hair CONTOUR, 5.6 → 10.7 off the cloak; the outer floret no longer within 4.9 px of the descending arm (its outline had been heal-trimmed open on both sides).
- hair parting: lock inner edges start at (376,157)/(385,157) instead of one point → ≥ 4.2 px of gold between them at the crown.
- ferrule: FAN_KW neck 36 → 50, root_dy 8 → −6 — plumes unchanged, the ferrule now sits OVER the plume roots (roots were on its rim; heal trimmed the ferrule's own outline/gold → paper nick). Heal actions 109 → ~63. (A ferrule halo was tried: unlined paper/jade edge, rejected.)
- hR: palm-view lowest fingertip lobe removed (HN.palm_tips on the frozen tucked hand).
- hR: jade strip + spur below the cuff → paper (HN.strip_to_paper, close 11) continuing the heel pocket to the band.
- hL: wrist dist 0.9 → 0.75 (back of the hand ≈ one block long; cuff follows).

## Iteration 2
- fan: the gown's and the bertha's left shoulder corners peeked into the 3–5 px V between plumes 0/1 (ink blot at 225–230, 346–354 after heal). `_plume_wedges` finds the narrow V gaps between two neighbouring plumes (away from the ferrule); gown + bertha are clipped out there, so the lining shows cleanly. (First attempt used a plain closing of the plume union: it also cut the gown along single-plume bends and exposed a red fleck at the ferrule — replaced.)
- sleeveR strip: close radius 8 → 11 so no jade dome is left on the band.

## Iteration 3
- bertha: pearls must stand ≥ 4.5 px clear of the plumes too (one was a paper half-disc on a plume outline).
- textile at the fan wrist: the one leaf crossing under the hand showed an edge stub + rung knot in the notch between the wrist and its wider cuff. Rejecting such leaves (tried: `no_show` / hard discs) removed half of the gown's textile (only 2 leaves per half) → rejected. Instead `HN.notch_stubs` drops, after compose, textile pieces < 14 px lying wholly within 12 px of a wrist/cuff corner; the leaf keeps its tips and body.
- `_qc_gown.leaf_pack`: optional `min_piece` / `no_show` (min_piece=90 in PACK; changes nothing now, guards slivers).
- soft region for the leaf packer uses the hands as drawn (tucked on the cuffs).

## Iteration 4 — final check + build
- Re-inspected at 750 / 188 / 3× / 6× / 10–24× (hands, knop, arms, ferrule, wedges, wrists, parting, face, crown, 180° copy): no new issues; HAND_LOG empty; heal actions 121 → 72.
- `deck.build QC` (limestone + white) and `deck.qa QC`: 13 pass, 0 fail, 1 warn ([12] 2 thin = HAIRLINE awns, 12 narrow-gap = acute plume/leaf tips, unchanged in count); balance paper 44.5 / red 11.5 / ink 18.5 / gold 10.2 / jade 15.3.
- Montage: build/review/courts2-QC/before-after.png (750, 188 ×2, 3× + 6× hand crops, 5× crops of the other fixes).
- Left for others / kit: palm-view lowest fingertip lobe touches the heel contour in courtkit.fist (all palm-view courts); patched locally only for QC.

# ROUND 2 (verifier findings: gown leaves lost on right half; sceptre-hand thumb too long; strip_to_paper white forearm; fan-side leaf tangent to hand; knop heal bites; far eye; colour balance)
Round-2 start copies: build/review/courts2-QC/work_r2/

## Round 2 — state found on resume (21:41; last edits 19:38, not logged)
Edits already in the files (vs work_r2/): PACK lengths + (110, 100), grid 2.0 (right-half leaves);
leaf_pack `sliver=` option (not yet used in PACK); HN.palm_fist (thumb rise/bow/taper, THUMB_R);
HN.sleeve_to_shaft replacing HN.strip_to_paper (sleeve runs on behind the culm below the cuff).
Next: rebuild, re-inspect, finish tangency / knop bites / eye / balance.

# ROUND 2 (continued, session 3 — 02:00)
Round-2 session-3 start copies: build/review/courts2-QC/work_r3/ (= the unlogged 21:41–22:15 edits).
## R2 it0 — inspection of the current files (r3/p0, preview + QA)
- QA [12] FAILS: 0.46 px gold fill at (541, 286.5) (knop_gold inset → hairline gold sliver) — must fix.
- balance: paper 44.2, jade 14.6, red 11.8, ink 19.1 (> 19 % ruling) — must fix.
- gown: right panel streams 3 whole leaves again (verifier's MAJOR fixed); left panel 1 leaf (passes under the fan arm; top piece's edge ends exactly on the cuff's upper-left corner — tangency).
- sceptre hand: new thumb (HN.palm_fist) reads as a thumb over the index at 750; the long white strip is gone (sleeve_to_shaft) but a white pocket remains right of the cuff (cuff ends at x 517, the sleeve below runs to the culm) → reads as the wrist continuing past the cuff.
## R2 it1 — knop, sceptre wrist
- knop: the unfinished `knop_gold` (gold cut, ink ring in halves) rendered PAPER inside the knop with a 0.46 px gold line (QA [12] ✗). Replaced by `knop_ink`: a 3.1 px Aquifer U-band inside the knop's LOWER half only (open at the top where it meets the silhouette ring's inner edge) — the gold is one clean inset, no bites, no nubs; no ears outside (a CONTOUR knop outline was tried: round ears at the lower corners — rejected).
- sceptre wrist: the paper pocket right of the cuff (cuff ended at x 517, the sleeve below ran to the culm) read as a wrist continuing past the cuff. Now: the cuff runs on behind the culm too (`sleeve_to_shaft(cuff_reach=True)`, its two arcs continued on their own circles; stacked before the culm; the sleeve's top edge runs on under it), and `HN.fill_heel` closes the notch between the heel, the culm and the cuff into the hand (the palm lies behind the culm in the palm view, so the wrist does too). Wrist variants a–j compared at 3×/1.5×: bend 60 / dist 0.8 / wrist 22 / cuff 28 (f) = compact fist on a steep forearm (45° / 26 / 32 made a big triangular mitten).
## R2 it2 — left leaf, ink, right-panel leaf tips
- left panel: with a corner rule (no visible leaf within 7 px of a cuff corner) the lattice finds NO leaf there (only 4 candidates exist, all the same leaf, all with the edge on the fan cuff's corner). The one leaf is placed by hand (`LEAF_L`, `leaf_pack(fixed=)`): L 115, S (6, −6), its outer edge entering the arm 9 px from the corner; a hatch rung left beside the sleeve edge (3 px cell) dropped (`notch_stubs` on `qc_cross`).
- fan cuff: the kit cuff's sides are straight while the sagged sleeve's edges are arcs — the sleeve stood 1.7 px proud of the cuff, the leaf was clipped there and heal cut it 3 px short of the arm. `HN.cuff_on_sleeve`: the cuff takes in the sleeve between its arcs.
- ink 19.04 % (unrounded; > the §10 19 % ceiling): plain red sleeves (folds=0, like K♣/Q♠/J♠/J♥) → 18.90.
- right panel: the middle leaf's narrow lower tip lay ON the sceptre sleeve's outline (hide_in 7: the chord end 8.8 px inside, the tip itself at the edge). hide_in 14 → the packer spreads the three leaves (one whole leaf under the bertha, two diving ≥ 20 px under the sleeve): lines join the sleeve edge cleanly (h18/h22 left free ends by heal — rejected). ink 18.81, jade 14.96.
- QA [12] raster narrow gaps: all 12 now at plume tips and ribbon-leaf tips (checked each at 12–16×); none at a hand.
## R2 it3 — left leaf lower piece, final
- left leaf at L 115 came out below the fan arm as an edge + a heal-trimmed midrib stub (a loose V). L 145 (same base / S): it comes out still wide — both edges, midrib, half-hatch — and runs on under the band (L 135 still left a free midrib end).
- LEAF_CLEAR 8/10 tried for the upper right leaf's tip (4 px under the bertha): the right panel then holds only 2 leaves — kept 6.
- removed unused HN.strip_to_paper / HN.ink_fillet.
- `deck.build QC` (limestone + white; deterministic: cards/QC.svg == preview md5), `deck.qa QC`: 13 pass, 0 fail, 1 warn ([12] raster: 2 thin = the sceptre's HAIRLINE awn, 12 narrow gaps = plume tips + ribbon-leaf tips, all ×2 by the 180° copy; none at a hand). Balance (unrounded): ink 18.86, gold 10.30, red 11.82, jade 14.91, paper 44.12. HAND_LOG empty; heal actions 58.
- Montage: build/review/courts2-QC/before-after.png (750, 188×2, 3× and 6× hand crops, gown 2×, knop / fan cuff / sceptre wrist / upper leaf tip / parting / ferrule).
- Left: far eye's outer corner joins the head contour (courtkit.face 3/4 convention, same as Q♦); the gown seam meets the sceptre hand's thumb-ball contour at ~30°; sub-px cap nubs where shaft outlines end under the kit hands; palm-view thumbs on K♠/K♣/K♦/Q♥ are still the kit's (QC's is local).

# ROUND 3 (consistency touch-up, 05:02): sceptre arms lost their lower outline (knop ink) + stray stub at (543–547, 243–248); QC R fist to use the kit's thumb bar (shorter than fingers); ink must stay ≤ 19 %.
Round-3 start copies: build/review/courts2-QC/work_r4/ (+ QC_card_start.svg = cards/QC.svg at 04:50).
## R3 it1 — sceptre arms, sceptre thumb, ink
- arms' lower outlines: heal groups consecutive same-style strokes as ONE <path>; the knop's Aquifer band (a FILL, role outline) sat between the sceptre's outlines and split that group, so the pedicels / arm outlines became separate pieces 1.3 px apart and heal cut the lower outlines away (and deleted a 6.2 px stub, leaving the one at 543–547, 243–248). `_qc_sceptre`: the knop band is emitted after every stroke (`knop_band`). Outlines back (box 490–540 × 240–258: 30.5 → 56.3 px of outline).
- tried: one outline round rachis + arms (a Y, gold running on into the arms) — splits the arm's two edges (2.9 px apart) into upper/lower pieces and heal deletes one of them: rejected.
- arm outlines end 0.3 px short of the rachis (clip `extra=rachis.buffer(0.3)`); pedicels start on the arm's / rachis's outline centre line (+0.3): no round nubs in the 2.9 px gold cores (they stood 0.5–1.5 px into them).
- QC R thumb: HN.palm_fist now uses the kit's thumb bar line for line (root 0.19 hb, tip 0.60 p, bow −1.6, crease x < 0.10 Lf) — the local rising thumb is gone; only the tip stops at 0.50 Lf (kit 0.56) so it ends at the culm's centre line, visibly shorter than the fingers (tried 0.56 / 0.50 / 0.46 at 6× and 1×). THUMB_R = dict(tip=0.50).
- ink with outlines back 18.97–18.98 → FAN_KW barb_room 0 → 1.5 (vane lines sweep out into the outline a few px sooner): 18.88; also removes the 4 plume-tip raster narrow gaps (uncapped count 46 → 38). (barb_room 3.0: 18.68 but lines broke into stubs — rejected.)
- p4 preview QA: 13 ✓, [12] warn (2 thin awn, 12+ narrow gaps: plume/leaf tips), balance ink 18.88 gold 10.25 red 11.82 jade 14.94 paper 44.12.
## R3 it2 — arm tips
- the arms' outlines were cut 0.5 px inside the tip florets: two round nubs in the floret's gold where the arm enters it (12×). Now clipped by U(knop, rachis, stone).buffer(0.3), eps 0: the caps end inside the rings. Stub at (543–547, 243–248) confirmed gone at 12× (the lower outline sweeps into the rachis). ink 18.87.
- checked, left as they are: the palm-view lowest fingertip lobe stays dropped on QC R (K♠/J♣ keep the kit's, which hooks onto the heel contour); sub-px cap nubs where the culm / fan-handle outlines end under the hands (kit STROKE_EPS, every court); the front plume's two vane lines end ~10 px above the ferrule (pre-existing).
## R3 it3 — verification + build
- re-inspected at 750 / 188 / 3× / 6× / 12× / 16×: both hands, the thumb, the arms (and the 180° copy), the knop, the ferrule, the fan, the crown, the face, white stock. Nothing new found. HAND_LOG is empty and heal made 47 changes (53 at the start of round 3).
- `deck.build QC` (limestone + white; cards/QC.svg md5 matches the p5 preview) and `deck.qa QC`: 13 pass, 0 fail, 1 warn. The warn is [12]: 2 thin (the HAIRLINE awn) and 12 narrow gaps shown (the list is capped at 12). The real count is 38, down from 46: the 4 plume-tip gaps are gone. The rest are plume and leaf tips, none at a hand. Balance: ink 18.87, gold 10.25, red 11.82, jade 14.94, paper 44.12.
- Montage: build/review/courts2-QC/before-after.png, made by r4/montage.sh. The round-2 montage is kept as r4/before-after_r2.png.
