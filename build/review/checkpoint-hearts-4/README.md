# Hearts checkpoint 4 (anatomy pass)

**Approval pending.** This reviews the anatomy pass on KH, QH and JH: every top-half
hand is now the correct hand of the correct arm, shown from the back, with a sleeve
that comes from the cloak. The other nine courts have not started. Nothing here is
approval.

## What to judge

Do all six hands read as **the figure's own left or right hand, back of the hand
toward us, thumb up the shaft, forearm leaving the cloak outward and down**? Then
decide on the four flags below.

## Flags for your decision

1. **hand5 wrap PALM view is the weakest back/palm read.** Its silhouette is the same
   as the other hand's back; only small crease cues tell them apart. A thenar-bulge
   silhouette change was not attempted, to protect the approved raw-hand look. Ask if
   you want a stronger palm read. (All six court hands use the back view, so no court
   shows a palm today. The palm view matters for the other nine courts.)
2. **Wrap thumb reads as a mitten** (hearts-anatomy-kh). The thumb is a small lobe, so
   chirality is hard to confirm from the silhouette alone. A more visible thumb or
   nail cue would be a hand5 kit change that affects every court. [closeup.png](closeup.png)
   shows four wrap hands at 12x so you can decide.
3. **QH stem sleeve is short** (hearts-anatomy-qh). Only about 35 px of sleeve shows
   before the robe outline clips it. Widening the mantle about 10 px on that side, or
   moving the stem stack left, would allow a longer sleeve.
4. **JH sleeve ends look slightly boxy** (user-testing). See the fiddle-hand sleeve.

## Files

| File | Content |
|---|---|
| [sheet.png](sheet.png) (1950 x 5091) | Per card: pre-mission (b4e26982) \| checkpoint 3 (90a950d4) \| now (b4561372) \| seam overlay. Then a reduced hand strip, the wrap L/R x back/palm specimen row, and density heatmaps with numbers. Flags are printed at the top. |
| [hands.png](hands.png) (2232 x 6650) | **Main focus.** Six rows, one per top-half hand, checkpoint 3 left and now right. Native 6x vector crops (`tools/zoom.py`), 180 x 150 card px (about 2.5x the hand), each captioned with its anatomy line. The crop window origin is printed on each crop; the hand moved on KH pole, JH fiddle and JH bow, so those windows differ between the two columns. |
| [closeup.png](closeup.png) | 12x crops of four wrap hands (KH pole, KH chalice, JH fiddle, JH bow) for the thumb question. |
| [matrix_wrap.png](matrix_wrap.png) | The wrap row of the hand5 L/R x back/palm specimen matrix. Order: L back, R back, L palm, R palm. The full matrix (all five poses) is `build/specimen/hand5_matrix.png`. |
| [evidence.json](evidence.json) | Commits, crop windows, density and QA numbers. |

The seam overlay is a diagnostic, never printed. Stock is limestone. Current PNG and
SVG are byte-identical to a fresh `tools/preview.py` run for all three cards.

## Anatomy per hand

"Figure's left" is on the viewer's right. All six are **back view**, hand size 0.82 of
face size, and none passes `cues=False`.

| Hand | Call | Fingertips point | Thumb | Forearm | Sleeve comes from |
|---|---|---|---|---|---|
| **KH pole** (viewer's right) | `hand5((500,470), -112, "wrap", L, back)` | left, toward the tunic | up, slightly left (pole's upper end) | 2.2 deg (nearly level, outward) | Red cloak's outer edge. Bell, run 84, fold lines, cuff line, cream pleats. |
| **KH chalice** (viewer's left) | `hand5((233.5,392), -90, "wrap", R, back)` | right, toward the tunic | up toward the bowl | 155.8 deg (down and out, left) | Red cloak's outer edge. Run 70, same cues. |
| **QH stem** (viewer's right) | `hand5((546,434), -90, "wrap", L, back)` | left, toward the body axis | up | 24.2 deg (down and out, right) | Jade mantle's outer edge. Run 40, about 35 px visible, two turn-back bands, no pearls. |
| **QH rest** (viewer's left) | `hand5((334,424), -24, "rest", R, back)` | right and slightly up | upper edge | 156.0 deg (down-left) | Jade mantle lobe over the bodice. Run 54, band plus pearls. **Unchanged from checkpoint 3 (control).** |
| **JH fiddle** (viewer's right) | `hand5((512,306), -90, "wrap", L, back)` | left | up the neck | 24.2 deg | Jade cloak shoulder. Own bell, run 50, flare 14, edge strokes, own hatch grain. |
| **JH bow** (viewer's left) | `hand5((253,392), -90, "wrap", R, back)` | right, toward the tunic | up | 155.8 deg | Jade cloak. Own bell, run 72, flare 12, edge strokes, hatch grain. |

Checkpoint 3 for comparison: KH pole and chalice were jade lapel/tunic openings (40 px);
QH stem and JH fiddle were right-hand **palm** views with the thumb down; JH bow was a
red tunic sleeve crossing the baldric.

## Composition changes made to fit the hands

- **KH.** The pole is steeper (lean 31.8 to 22 deg from vertical) so the forearm leaves
  the wrist outward. Pole grip moved from (527.4, 467.9) to (500, 470). Chalice grip
  394 to 392, now R/back, thumb up. Both sleeves changed from jade lapel lobes to
  **red cloak sleeves** ending at the cloak silhouette (fold lines, cuff line,
  cream pleats). Pole length and bands are the same, re-aimed. Chalice, bubbles, seam
  unchanged.
- **QH.** Stem hand changed from right/palm to left/back and shrunk to 0.82 of face
  size (it was 22% bigger, now matches the resting hand). Its sleeve now runs from the
  mantle's outer edge (run 44 to 40, neck 4 to 10) and two turn-back bands replace
  band plus pearls. Stem, leaf, flower and seam unchanged. Resting hand unchanged.
- **JH.** Fiddle moved 18 px left (x 530 to 512) and 40 px down (body top 296 to 336);
  the hand moved 280 to 306 so the cloak shoulder is wide enough for an outer sleeve.
  Bow hand 380 to 392 and changed from a wrongly drawn left hand to R/back. Both
  sleeves are now the jade cloak's own (the bow sleeve was red tunic over the baldric);
  the old red sleeve, raised fold hull and fiddle contact patches were removed. The
  ripple-slash group was re-centred with smaller radii and the right-hand slash groups
  dropped, because the fiddle body now fills that jade.

## Per card summary

| Card | Seam (unchanged) | Hands and attributes | Scene items (pre -> cp3 -> now) |
|---|---|---|---|
| **KH** | `SEAM = -20` | Pole plus chalice with five bubbles. | 26 -> 10 -> **10** |
| **QH** | `SEAM = -42` | Sagittaria stem plus hand resting on the red scale bodice. | 42 -> 4 -> **4** |
| **JH** | `SEAM = -24` | Fiddle plus upright bow. | 26 -> 4 -> **4** |

## QA

Fresh `tools/preview.py art/<ID>.py <ID> --qa` this session: all three **15 pass, 0 fail,
1 warn** (check 12, raster). Checks 10a, 10b, 10c, 10s clean. 10s seam length and broken length:
KH 500.2 / 0.0 px, QH 632.4 / 0.0 px, JH 514.5 / 0.0 px.

| Card | Check 12 warning | Gold / balance notes |
|---|---|---|
| KH | ink: 4 narrow-gap regions | gold 9.8% |
| QH | red: 10 and ink: 12 narrow-gap regions | gold 7.9% (check 5 passes) |
| JH | red: 2 thin; ink: 2 narrow-gap regions | jade 12.8%, ink 18.6% |

## Density versus pre-mission (b4e26982)

`tools/density.py <ID> --ref b4e26982`, court art only. Higher score is denser; the
low-detail fraction is the share of 24 px tiles below the floor.

| Card | Score | Low-detail fraction | Largest flat core (px2) |
|---|---|---|---|
| KH | 0.353 -> **0.391** | 0.082 -> **0.0021** | 4116 red -> **1102 gold** |
| QH | 0.373 -> **0.380** | 0.016 -> **0.0057** | 1967 red -> **757 gold** |
| JH | 0.315 -> **0.389** | 0.141 -> **0.0214** | 11145 red -> **596 jade** |
