# Hearts direction checkpoint

**Approval pending.** Review KH, QH and JH before reworking the other nine
courts. This folder presents the validated Hearts pilot; it does not approve
the direction or change the artwork.

## Review images

- [sheet.png](sheet.png), **2346 × 4662**: KH, QH, JH from top to bottom;
  **before | after | seam overlay** across each row, followed by the hand strip.
- [hands.png](hands.png), **2346 × 886**: the three retained grips at native
  **6× vector-rendered resolution**, left to right KH, QH, JH.
- [seams.png](seams.png), **2346 × 886**: unannotated centre/robe-join crops at
  native **6×**, in the same order.

Open the sheet at full resolution to compare the cards. The coloured guides
in its third column are **diagnostics only**, not lines printed on the cards.
The actual joins have no band, partition line or centre medallion. All images
use limestone stock. The complete folder is under 3 MB (15 MB limit).

**Before:** original committed PNGs from `b4e26982:build/png/<ID>.png`.
**After:** committed `build/png/<ID>.png` at `54a9da9d`, the completed Hearts
pilot. Fresh sandbox SVGs and PNGs matched these production files
byte-for-byte during checkpoint verification.

## Per-card decisions

| Court | Seam choice | Kept in the one hand per half | Secondary disposition | Scene items, before → after |
|---|---|---|---|---|
| **KH, Ferryman King** | `SEAM = -20`, diagonal through the broad continuous robes, clear of the portrait and pole grip | Punting pole on the viewer's right, passing behind the head | Chalice and its bubbles dropped; secondary forearm omitted. No floating chalice or unsupported second grip remains. | **26 → 8** |
| **QH, Aquamaid Queen** | `SEAM = -42`, steeper diagonal through the drapery, avoiding the portrait/grip and scale-course microfragments | Upright sagittaria stem, arrowhead leaf and flower | Second bodice hand removed, with the old forearms, armlets and bracelets. There was no second held object to re-home. One pearl collar strand remains. | **42 → 4** |
| **JH, Spring Minstrel** | `SEAM = -24`, diagonal through sleeves and robes; the baldric is not a divider | Upright fiddle held by its neck on the viewer's right | Bow retained upright/parallel at `x246`, shortened to `y422`, tucked under a baldric tab near `y330`. Former bow hand removed. The wearable support keeps it from floating or crossing the fiddle. | **26 → 4** |

Counts are `len(figure().items)` **after assembly/merging, before composition
and deck clipping/180° duplication**. They include `sil=False` entries, not
SVG paths, ink plates or individual fingers. Both sides were measured for
this checkpoint: before from the actual `b4e26982` art/kit snapshot, after
from the current modules. Planning estimates of KH 21 / QH 35 are not used.

All three use the shared five-finger hand primitive and an integrated
hand-and-sleeve contour. Each top figure has one hand; its inverted copy
provides the other. Integration consolidates garments and held attributes
instead of using a centre badge or stacked paper-halo patches.

## QA summary

Fresh `tools/preview.py ... --qa` runs for this checkpoint reported
**45 pass, 0 fail, 3 warnings** in total:

| Court | Pass / fail / warn | 10a, 180° symmetry | 10b, band removal | 10s, seam continuity | Gold area |
|---|---|---|---|---|---|
| KH | **15 / 0 / 1** | Difference `0` | Band, partition, medallion all `0` | No breaks; legacy-cut width `0` | **9.0%** |
| QH | **15 / 0 / 1** | Difference `0` | Band, partition, medallion all `0` | No breaks; legacy-cut width `0` | **7.7%** |
| JH | **15 / 0 / 1** | Difference `0` | Band, partition, medallion all `0` | No breaks; legacy-cut width `0` | **11.0%** |

All three rendered as **art**, not placeholders. Stroke, palette,
hidden-plate and other applicable machine checks passed. Each uses all four
inks and stays below the 15% gold cap. Direct seam-overlay checks also found
**0.0 px broken** over KH **500.2 px**, QH **632.4 px** and JH **514.5 px**.

The three warnings are **check-12 raster heuristics**, not failures:

- **KH:** four narrow-gap regions at intentional gold-hair tapers outside
  the face, near eye level. These are not eyelid terminals.
- **QH:** four narrow-gap regions at connected acute face/rim and cap
  vein/perimeter junctions.
- **JH:** two acute red textile tips flagged as thin, and two deliberately
  open tuning-peg notches flagged as narrow ink gaps.

The prior Hearts pilot zoom review inspected these warnings and found no
vector defects. Independent pilot user testing passed **15/15 assertions**;
all three scrutiny feature reviews passed. The checkpoint itself was viewed
at full-card, seam-overlay and 6× crop scale. It is not a substitute for the
later full-deck polish/publication pass.

QH's first checkpoint QA run exceeded a 180-second timeout while three
cards ran together. It was rerun alone with a 420-second limit and completed
successfully. No artwork change was needed.

## Crop coordinates and source commands

Coordinates are `x y width height` in the card's **750 × 1050 SVG units**.
Each crop is **125 × 120 units**, rendered directly from vectors to
**750 × 720 pixels**, not enlarged from the card PNG.

| Card | Retained-hand crop | Centre/robe-join crop |
|---|---|---|
| KH | `470 399 125 120` | `310 465 125 120` |
| QH | `470 380 125 120` | `310 465 125 120` |
| JH | `455 210 125 120` | `310 465 125 120` |

Run from the repository root, writing intermediate evidence outside the
repository:

```sh
mkdir -p /tmp/checkpoint-hearts/before
for id in KH QH JH; do
  git show "b4e26982:build/png/$id.png" > "/tmp/checkpoint-hearts/before/$id.png"
  .venv/bin/python -m deck.frames seam "cards/$id.svg" \
    --module "art/$id.py" --out "/tmp/checkpoint-hearts/$id-seam.png"
  .venv/bin/python tools/preview.py "art/$id.py" "$id" \
    "/tmp/checkpoint-hearts/qa/$id" --qa
  .venv/bin/python tools/zoom.py "cards/$id.svg" \
    310 465 125 120 6 "/tmp/checkpoint-hearts/$id-blend.png"
done
.venv/bin/python tools/zoom.py cards/KH.svg 470 399 125 120 6 /tmp/checkpoint-hearts/KH-hand.png
.venv/bin/python tools/zoom.py cards/QH.svg 470 380 125 120 6 /tmp/checkpoint-hearts/QH-hand.png
.venv/bin/python tools/zoom.py cards/JH.svg 455 210 125 120 6 /tmp/checkpoint-hearts/JH-hand.png
```

The comparison panels retain the original 750 × 1050 before/after PNGs.
Only the 1500-pixel-wide diagnostic overlays are reduced to the same panel
size. The sheet uses 24-pixel gutters, labelled rows and columns, the native
6× hand strip, and a QA footer; ImageMagick appends the labelled sections.
The hand and join strips preserve the crop pixels without rescaling.

`preview.py --qa` can write `build/qa/flags/`; its generated flags were not
included in this checkpoint commit. Source art and production renders were
left unchanged.

## Approval requested

Confirm the **continuous robe join**, **five-finger grip direction**,
**one hand per half** and the **secondary-attribute dispositions** above
before proceeding to Spades, Clubs and Diamonds. No outstanding pilot
defect is recorded. This is the deliberate user-review pause, not approval.
