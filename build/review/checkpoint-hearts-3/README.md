# Hearts checkpoint 3 (cuff fix)

**Approval pending.** This is a review of the KH, QH and JH cuff fix made after
your checkpoint 2 feedback. The other nine courts have not started. Nothing
here is approval.

## What to judge

Do the six top-half cuffs now read as **the end of a sleeve coming out of the
cloak** (checkpoint 2 had small separate cuff stubs)? Two points need your
call:

1. **QH stem hand.** The sleeve is only about **37 px** inside the jade
   mantle. It has a turn-back band and a pearl row but **no wave pattern**
   (the wave field is the mantle's jade inset 10 px, so a sleeve under ~45 px
   cannot hold waves behind its band and pearls). Does it read as a sleeve?
2. **KH, both hands.** The cuffs read as the **jade lapel/tunic edge opening
   round the wrist (a sleeve of the tunic)**, not as a bell sleeve of the
   **red cloak**. Is that acceptable, or should the red cloak own the sleeves?

## Files

| File | Size | Content |
|---|---|---|
| [sheet.png](sheet.png) | 1950 x 4587 | Per card: pre-mission (b4e26982) \| checkpoint 2 (18b4c73f) \| now (48f0d156) \| seam overlay. Then a reduced hand strip and the density heatmaps with numbers. Both flags are printed at the top. |
| [hands.png](hands.png) | 2244 x 6112 | **Main focus.** Six rows, one per top-half hand, checkpoint 2 on the left and now on the right. Native 6x vector crops (`tools/zoom.py`), 180 x 150 card px each, about 2.5x the hand size. |
| [evidence.json](evidence.json) | small | Source commits, crop windows, density and QA numbers. |

Stock is limestone. The seam overlay is a diagnostic, never printed. Folder
is under 5 MB. Seam overlay source: `cards/<ID>.svg` with `--module art/<ID>.py`.
Current PNG, SVG and fresh `tools/preview.py` output are byte-identical for all
three cards.

## Where each sleeve comes from

All six sleeves are a short bell region of a neighbouring garment, unioned into
that garment's fill. They share its outline, carry its pattern, have a mouth
curved convex toward the hand and a bold turn-back band. None is longer than
the 90 px limit, and no forearm is drawn.

| Hand | Sleeve source | Run | Notes |
|---|---|---|---|
| **KH pole hand** (viewer's right) | **Jade lapel/tunic edge** opens round the wrist. | 40 px | **Flag 2.** The grip was flipped to approach from the tunic side (now R/back, grip (527.4, 467.9), 14 px further along the unchanged shaft) so the sleeve is jade, not a stub on red. Jade scales carry onto the sleeve. |
| **KH chalice hand** (viewer's left) | **Jade lapel/tunic edge**, as above. | 40 px, bell 5 | **Flag 2.** Hand and chalice unchanged at (233.5, 394). Bubbles and chalice stay. |
| **QH stem hand** (viewer's right) | **Jade mantle.** The hand is already on the mantle, so the sleeve is clipped to it and enters through the mantle contour with its own two side lines. | 44 px, about **37 px visible inside the mantle** | **Flag 1.** Narrow tube (bell 4, neck 4). Band plus pearls, no waves. Stem, leaf and hand did not move. |
| **QH bodice-resting hand** (viewer's left) | **Jade mantle.** A bell lobe stands off the mantle edge over the red bodice. The bodice contour is the lobe's outline. | 54 px | Hand moved 12 px right, from (322, 424) to **(334, 424)**, to give the lobe room (still more than 50 px from the seam). Band plus pearls. |
| **JH fiddle hand** (viewer's right) | **Jade mantle shoulder.** The raised mantle fold and the sleeve are joined by one convex hull, so the shoulder rises in a single edge into the cuff mouth. | 44 px, bell 12 | Jade hatch carries onto the sleeve. Hand and fiddle did not move. |
| **JH bow hand** (viewer's left) | **Red tunic.** The wrist points into the tunic, so a red hatched sleeve crosses the cream baldric from the tunic to the hand. | 58 px | The sash is interrupted locally. Festoon and seam layout unchanged. Hand and bow did not move. |

My reading of the strip, for your check: JH and QH-resting show the clearest
sleeve ends. QH-stem is the shortest and plainest. KH's sleeves are small
jade openings hugging the wrist, which is exactly why flag 2 asks you.

## Per card summary

| Card | Seam (unchanged) | Hands and attributes | Scene items (pre -> cp2 -> now) |
|---|---|---|---|
| **KH** | `SEAM = -20` | Pole (back of hand) plus chalice with five bubbles. | 26 -> 8 -> **10** |
| **QH** | `SEAM = -42` | Sagittaria stem plus hand resting on the red scale bodice. | 42 -> 4 -> **4** |
| **JH** | `SEAM = -24` | Fiddle plus upright bow. | 26 -> 4 -> **4** |

## QA

Fresh `tools/preview.py art/<ID>.py <ID> --qa`, run this session:

| Card | Result | Warning (check 12, raster) |
|---|---|---|
| KH | 15 pass, 0 fail, 1 warn | 4 narrow ink gaps (approved eye corners) |
| QH | 15 pass, 0 fail, 1 warn | 10 red + 12 ink narrow gaps, inside hand fingertip slits and eye corners |
| JH | 15 pass, 0 fail, 1 warn | 4 narrow ink gaps (same as baseline) |

Checks 10a, 10b and 10s are clean on all three: `10s` seam lengths are KH 500.2 px,
QH 632.4 px and JH 514.5 px with **0.0 px broken**. The milestone validators
also ran full `deck.qa all` (650 pass, 0 fail) and the test suite (104 passed)
at HEAD.

## Density versus pre-mission (b4e26982)

Fresh `tools/density.py <ID> --ref b4e26982`, court art only. The score is
detail-edge density. Low-detail fraction is the share of 24 px tiles below
0.12. Flat patch is the eroded core. Limit `T_patch` = 6262.25 px².

| Card | Score, original -> now | Low-detail fraction | Largest flat core |
|---|---|---|---|
| KH | 0.3528 -> **0.3954** (cp2 0.3887) | 8.18% -> **0.21%** | 4116 red -> **1102** gold px² |
| QH | 0.3727 -> **0.3779** (cp2 0.3767) | 1.61% -> **0.57%** | 1967 red -> **757** gold px² |
| JH | 0.3154 -> **0.3979** (cp2 0.3947) | 14.11% -> **0.95%** | 11145 red -> **511** jade px² |

Every card is denser than the original and every flat core is far below
`T_patch`.
