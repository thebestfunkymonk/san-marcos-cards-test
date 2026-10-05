# v3-hands progress

## iter 0 — survey
- read courtkit §7 (Hand, fist, cup, flat, helpers), tools/hand_specimen.py, Drifters refs (Q♠ fist, K♥ card hand: one paper silhouette, open finger lines from the tip notches, thumb merged).
- backup of the pre-v3 kit: build/review/v3-hands/courtkit-before.py
- plan: develop the new §7 in a dev file, splice it between the §7/§8 headers of deck/courtkit.py (only my section), keep helper names (_edge, _qbez, _crease, _rigid, _xf, _to_local, _vec, _unit, _junction_smooth used by art/_*_hands.py), fist_geom/fist_wrist keys.

## iter 1 — new §7 written and spliced (dev copy: build/review/v3-hands/sec7_dev.py; splice tool replaces only §7)
- one silhouette per hand, five digits; _digit (tapered disc hulls), _webs (fill wedges between tapered neighbours behind the tips → clean V notches), _open_line (lines start ON the outline, end free), _biggest (holes filled).
- fist: tapered fingers, round tips (r = 0.5 band), fan, stagger (middle longest), knuckle ridge; thumb='over' (thenar flows into back of hand, open crease 68% from tip) | 'behind' (tip peeks over the index lobe; weak); palm view = curled fingertip arcs just past the shaft's near edge.
- pinch (= fist grip='pinch'): index curls 0.3 hb past a thin stem, others stepped back; thumb tip on the stem's near side.
- cup: size-tied fingers (reach 0.40 size), spread 1.10, thumb on the rim, web closed below the rim contact; crease lines removed.
- flat/open_hand: convex palm hull (hypothenar), tapered fingers, thumb CMC→MCP→tip bending back, smooth web; palm view life-line arc round the thenar, kept ≥ 6.3 px from other lines.
- Hand.silhouette(run) / Hand.with_sleeve(sleeve) → one continuous outline + MEDIUM cuff line.
- wrist_w default None → scales with size. hand_size(face). hand(pose, ...) dispatcher.
- tools/hand_specimen.py rewritten: 13 rows (every pose × L/R × sizes 70/85/100, angles, merge row), --courts optional.
- QA (scratch check.py: heal_log + qa.vector_gaps per cell): 0 vector gaps; remaining heals are orb latitudes/shaft fill vs fingers (attribute side).

## iter 2 — verified
- all 12 courts build (`deck.build KS … JD`, exit 0, no tracebacks); their look changed only through the kit (court-local hand helpers untouched).
- specimen regenerated: build/review/v3-hands/specimen.png (3× + card size), specimen_1x.png, specimen_calls.json; `--courts` mode checked (build/review/v3-hands/courts/).
- DONE for this job; open items in the return summary (weaknesses).

## round 2 (reviewer findings) — iter 3
- grip rebuilt: thumb = top edge (back view: wedge flush with the index top at the shaft's near edge, rising to the back; one branch crease from the tip to ≤ the knuckle line; palm view/pinch: the thumb is the fist's top band, tip lobe in the fingertip column, crease from the notch); palm view: finger lines stop at the shaft's near edge, no tip arcs/hooks; little finger tilted up 8°, full round lobe; underside = ONE curve from the little fingertip's lowest point into the wrist (no straight run, no floor box); ridge clipped under the little finger's lower edge; notch lines start where the outline strokes' inner edges meet (_trim_start / _notch_lines); _clean (opening r 2 + closing) for spurs.
- Hand.add_to(halo=0) now registers LINE_TUCK with halo_zone = hand.buffer(-MEDIUM/2): lines behind end under the hand's outline stroke (no cap bumps).
- pinch: index crosses the stem (reach 0.14 hb), thumb band tip at the stem, lower three fingers curled and stepped back (carve) — ground and stem visible below.
- cup rebuilt: palm under the orb, 4 short tips over the lower rim, thumb lobe to the rim at thumb_to+8°, thenar hull into the wrist.
- flat rebuilt: fingers ≈ 45 % of length, lines to near the knuckles, thumb opens from mid-palm on a kept-open V (40° in open_hand), life line from the web round the thenar.
- fist_wrist default dist 1.0 → 0.85; wrist 0.68 hb.
- specimen: PIL sheet assembly (no magick drift), --courts crops every 'hand…' item from each court's composed art (court-local helpers included); pinch rows use tilted stems; grip row has axis 180 / 0 bars.
- splice tool: build/review/v3-hands/splice.py (dev → deck/courtkit.py §7). Round-1 dev copy: sec7_dev_round1.py.

## round 2 — iter 4 (done)
- back-view thumb crease = one quadratic branch from the top contour (5.5 px clear of the shaft edge) to ≤ the knuckle line; 'behind' thumb = a lobe beside the index tip, flush with the top, no crease.
- open hand: curl foreshortens fingers (in-plane sweep 0.45×), thumb free part ≈ 0.62–0.70 middle finger, last joint 8°, thenar mound kept small (no kink).
- cup: fingertips either stay 6 px under the kit orb's lowest ripple latitude or (small orbs) pass over it with the notches above it (latitude hidden index→little, never dashed); thumb kept under it in 'above' mode (clear_y param; None disables).
- QA (scratch check.py): 80 cells, 0 vector gaps; heal log = specimen sleeve/cuff fill slivers + one gold sliver (pinch size 70 stem); no latitude heals.
- 12 courts build (exit 0); courts sheet: build/review/v3-hands/courts/specimen*.png (25 court hands incl. court-local helpers).

## round 2 — iter 5 (resume check)
- confirmed deck/courtkit.py §7 == sec7_dev.py (splice current); specimen regenerated (80 hands, 3x + 1x) and re-inspected: grip/cup/open rows unchanged and sound.
- 12 courts rebuilt (exit 0, no tracebacks); deck.qa on the 12: 173 pass, 0 fail, 7 warn (raster narrow-gap 'gaps' warnings on KS QS JS KH KC QC QD — court art, not triaged per hand).
- job complete; returning summary.
