# Hearts checkpoint 2

**Approval pending.** Review these reworked Hearts before the other nine
courts begin. This checkpoint presents the validated artwork, not approval.
It supersedes checkpoint 1's rejected one-hand/long-arm direction.

## Review images and provenance

- [sheet.png](sheet.png), **1800 × 4170**: KH, QH, JH rows, each ordered
  **pre-mission | checkpoint 1 | now | seam overlay**. Below are all six
  top-half hands, unmarked robe joins and the density comparison.
- [hands.png](hands.png), **2400 × 3120**: both top-half hands per card,
  left panel tall attribute, right panel restored secondary. These are
  **native 6× vector crops**, not enlarged card PNGs. Every crop includes
  the full hand, short cuff and surrounding patterned garment.
- [seams.png](seams.png), **2400 × 990**: unmarked joins, sourced at 6×
  and reduced to fit the strip.
- [density.png](density.png), **2400 × 1200**: baseline/current heatmaps
  with numbers. Yellow means low-detail tiles, magenta means eroded flat
  ink cores, cyan means informational paper regions.
- [evidence.json](evidence.json): source PNG hashes, revision IDs, crop
  coordinates, layout boxes, full density metrics and fresh QA checks.

All art is on limestone stock. The overview reduces the 2400-pixel-wide
assembly to 1800 pixels; open the standalone strips for detailed inspection.
The folder is about **9 MB**, below the 15 MB limit. Coloured seam guides are
**diagnostics only**, never printed dividers.

Sources:

| Column | Source |
|---|---|
| Pre-mission | Committed `b4e26982:build/png/<ID>.png` |
| Checkpoint 1 | Committed `7774b626:build/png/<ID>.png` |
| Now | Production `build/png/<ID>.png` at `56bcea8c` |
| Seam overlay | Production `cards/<ID>.svg`, with explicit `--module art/<ID>.py` |

Current card revisions are KH `541d0f8e`, QH `11cc7cd9`, JH `56bcea8c`.
Fresh sandbox SVGs and PNGs matched production byte-for-byte for all three.
No production artwork or earlier checkpoint was changed for this review.

## Both hands and their emergence

Each figure now has **two shared `courtkit.hand5()` hands per half**, four
hands on the complete double-headed card. The forearms remain inside the
drapery. Each card shapes its own local garment folds/cuffs, without a
shared arm-routing helper, long visible arms or paper grip halos.

| Court | Approved seam, unchanged | Viewer's-right tall-attribute hand | Restored secondary hand |
|---|---|---|---|
| **KH, Ferryman King** | `SEAM = -20`, through continuous robes | Wraps the punting pole, which passes behind the head. A **20 px patterned jade cuff** opens directly from the robe beside the pole; hand and cuff share an outline. | Wraps the restored original chalice stem beside the mantle. A **24 px patterned jade cuff** meets the nearby scalloped garment. The chalice and **five bubbles** return; no secondary substitution. |
| **QH, Aquamaid Queen** | `SEAM = -42`, steeper diagonal through drapery | Wraps the upright sagittaria stem. A **24 px pearl-trimmed, hatched cuff** opens from the wave robe next to the stem, not from a reaching arm. | Restores the hand resting on the red scale bodice. Its **24 px pearl-trimmed gown cuff** merges locally into the garment. Wrist moved from `(300,452)` to `(322,424)` to clear the unchanged seam; the gesture is retained. |
| **JH, Spring Minstrel** | `SEAM = -24`, through mantle and robes | Wraps the fiddle neck. A **raised, patterned mantle fold** meets the short **24 px cuff** immediately below the grip, with a shared hand/cuff outline. | Wraps the restored upright bow near the robe's left fold through a short **24 px patterned cuff**. The old long sleeve and bow-support tab are gone; the bow is held, not left floating. |

**JH accommodation to note for approval:** original bow head/frog/button
geometry is restored at the approved pilot's `x246`. To clear the unchanged
seam, the frog and button move upward **40 px**, from `y454/y490` to
`y414/y450`; the tip remains `y112`. The bow stays parallel to, and separate
from, the fiddle.

Detail is integrated into garments: KH ripples, scallops and central
hatching; QH scales, waves, pearls and local hatching; JH mantle/tunic
hatching, complete ripple courses and fiddle detail. Pattern does not rely
on extra stacked pieces. Both halves inherit the same density by C2 copying.

## Density versus pre-mission

Fresh `tools/density.py <ID> --ref b4e26982` runs measured **court art only**,
excluding frame, corner indices and historical band/medallion decoration.
The score is detail-edge density; low-detail fraction is the fraction of
eligible 24 px tiles below `0.12`. Flat patch area is the **eroded core**
after a 5 px erosion, not the raw garment area. Cyan paper is informational,
not a failing flat-ink patch.

| Card | Score, original → now | Low-detail fraction, original → now | Largest flat core, original → now |
|---|---|---|---|
| KH | **0.352754 → 0.388713** | **0.081761 → 0.002058** (8.1761% → 0.2058%) | **4116 red → 1102 gold px²** |
| QH | **0.372674 → 0.376747** | **0.016097 → 0.007648** (1.6097% → 0.7648%) | **1967 red → 757 gold px²** |
| JH | **0.315374 → 0.394663** | **0.141104 → 0.013359** (14.1104% → 1.3359%) | **11145 red → 511 jade px²** |

All three pass: score is at least baseline, low-detail fraction is no worse,
and largest flat core is below the frozen **T_patch = 6262.25 px²**.
Heatmaps are a diagnostic aid, not a substitute for the zoomed garment review.

## Integration and Scene counts

| Card | Pre-mission `b4e26982` | Checkpoint 1 `7774b626` | Now `56bcea8c` |
|---|---:|---:|---:|
| KH | **26** | **8** | **10** |
| QH | **42** | **4** | **4** |
| JH | **26** | **4** | **4** |

Counts are `len(figure().items)` after assembly/merging, before composition,
clipping and 180° duplication, including `sil=False` entries. They are not
SVG paths, fingers or pattern marks. KH's two additional entries restore the
chalice and bubbles; QH/JH integrate the restored hands into existing items.

## QA summary

Fresh sandbox preview QA for this checkpoint: **45 pass / 0 fail / 3 warnings**.

| Card | Pass / fail / warn | 10a C2 difference | 10b band / partition / medallion | 10s broken / legacy-cut width | Gold area |
|---|---|---|---|---|---|
| KH | **15 / 0 / 1** | `0` | `0 / 0 / 0` | `0 / 0 px` | **9.9%** |
| QH | **15 / 0 / 1** | `0` | `0 / 0 / 0` | `0 / 0 px` | **7.8%** |
| JH | **15 / 0 / 1** | `0` | `0 / 0 / 0` | `0 / 0 px` | **10.5%** |

All render as art, use four inks and meet the gold cap. Applicable stroke,
palette and hidden-plate checks pass. Direct overlays also report zero
broken seam pixels over KH **500.2 px**, QH **632.4 px**, JH **514.5 px**.

The three warnings are existing **check-12 raster heuristics**, not failures.
All have zero vector defects and zero raster-thin regions:

- **KH:** four intentional near-eye narrow gaps, including inverted copies.
- **QH:** four red and twelve ink narrow gaps at connected hand notches,
  thumb/cuff transitions and shared outline junctions.
- **JH:** four ink narrow gaps at connected cuff contours and tuning-peg notches.

Prior Hearts-rework zoom reviews inspected these contacts and accepted them.
This checkpoint viewed both hands and robe joins directly at vector-crop
scale. The previously completed milestone scrutiny, **not rerun here**,
reported **104 tests passed**, compilation exit 0 and full-deck QA
**650 pass / 0 fail / 12 raster warnings**. This is not the later polish or
publication pass.

## Crop coordinates and diagnostic commands

Coordinates are `x y width height` in the **750 × 1050 SVG units**.
Hand boxes are approximately twice the hand extent, with fold/cuff context.

| Card | Tall hand | Secondary hand | Unmarked robe join |
|---|---|---|---|
| KH | `450 380 160 140` | `170 323 160 140` | `145 420 465 225` |
| QH | `445 365 160 140` | `250 343 180 145` | `145 300 465 450` |
| JH | `445 205 160 140` | `185 310 160 140` | `145 405 465 240` |

Hand images are 960 × 840 px, except QH's secondary at 1080 × 870 px,
all pasted into `hands.png` unscaled. Join images are sourced at 6× and
reduced to 740 px wide in `seams.png`. The four comparison columns use
540 × 756 px cells before the overview reduction.

Run source diagnostics from the repository root. Run QA sequentially to
avoid resource contention:

```sh
mkdir -p /tmp/checkpoint-hearts-2
for id in KH QH JH; do
  mkdir -p "/tmp/checkpoint-hearts-2/$id"
  git show "b4e26982:build/png/$id.png" > "/tmp/checkpoint-hearts-2/$id/before.png"
  git show "7774b626:build/png/$id.png" > "/tmp/checkpoint-hearts-2/$id/checkpoint1.png"
  .venv/bin/python -m deck.frames seam "cards/$id.svg" \
    --module "art/$id.py" --out "/tmp/checkpoint-hearts-2/$id/seam.png"
  .venv/bin/python tools/density.py "$id" --ref b4e26982 \
    --out "/tmp/checkpoint-hearts-2/$id/density"
  .venv/bin/python tools/preview.py "art/$id.py" "$id" \
    "/tmp/checkpoint-hearts-2/qa/$id" --qa
done
# Repeat this form with each box in the table:
.venv/bin/python tools/zoom.py cards/KH.svg \
  450 380 160 140 6 /tmp/checkpoint-hearts-2/KH/hand-0.png
```

The labelled sections are composed with Pillow and appended with ImageMagick.
`preview.py --qa` can write `build/qa/flags/`; those session side effects
were restored/removed and are not included in the checkpoint.

## Approval requested

Confirm **two hands per half**, **short integrated cloak cuffs/folds**,
**restored secondary attributes/gesture** and **dense, even garment detail**,
including JH's bow accommodation, before starting Spades, Clubs or Diamonds.
The approved continuous joins, seam angles and overall layouts remain intact.
