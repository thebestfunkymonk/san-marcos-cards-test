# corr JOKER_BLACK progress (Trickster: beak/crown overlap + alignment)

## iter 0 — baseline (2026-09-24)
- Backup of original art: scratchpad orig/ (art/JOKER_BLACK.py, art/_joker_black_*.py).
- Before (old build, caption at 785): content bbox x 48.8-701.2, y 109.2-785.2 (mid 447.2), centroid (384.9, 451.5).
- Before (new frames, caption lowered 72, figure unmoved): y 109.2-857.2 (mid 483.2), figure bottom 639.2 (gap to rule 762 = 122.8), figure centroid (385.7, 401.2).
- Crown: pivot at band's left end on bill tip, swing 52 deg; bill in front, crown cut 4.2 clear of bill -> left point mangled, left jewel lost.
- Plan: crown IN FRONT at the crossing (bill broken 4.2 px clear of the band, i.e. bill passes behind the near side of the ring, tip threaded through at the band's left end); crown fully intact. Alignment via a rigid Frag.translate of the figure (wire ends pre-offset so the wire stays symmetric about 375).

## iter 1 — crown threaded, figure shifted (draft previews in scratchpad it1/, it2/)
- props: COR_PIVOT -> COR_HOOK (-24,-2) placed COR_HOOK_S=24 px down the bill axis; COR_SWING kept 52. coronet() drawn whole; new coronet_hull() (jewels filled).
- JOKER_BLACK.build: ink solid differenced by coronet_hull().buffer(4.2) (bill passes behind band's lower-left end; tip piece 29.9 px2 emerges past the band end). Crown no longer cut at all.
- Placement: props.FIG_SHIFT = (-8, 73) applied with Frag.translate to jade+gold+ink figure (caption untouched). Wire ends drafted at 52+8 / 698+8 so on card they are 52 / 698; bulbs drafted at card x +8 so they stay at 175/560/655.
- it2 measured: all bbox x 48.8-701.2 y 193.2-857.2 mid (375.0, 525.2), alpha centroid (378.7, 525.2); figure y 193.2-712.2, gap to rule 49.8; bird+crown area centroid x 375.2.
- Preview QA: all hard checks pass; check 12 vector/raster empty.
- Next: deck.build both stocks, deck.qa, review renders/crops into build/review/.

## iter 2 — built + QA (final)
- `deck.build JOKER_BLACK` (limestone) and `--stock white` built; `deck.qa JOKER_BLACK`: 12 pass, 0 fail, 0 warn (strk pal budg hide g/r idx safe clr gaps svg rndr wht all ✓; 10c min clear 75.0; 12 vector/raster empty).
- Output-path checks (cards/JOKER-BLACK.svg): coronet = one gold polygon, 3 jewel holes, area 1077.6 vs whole 1077.5 (before: 949.8, 2 jewels, 127.7 px2 cut away); min distance ink -> coronet 4.19 (flattening of 4.2); ink ∩ coronet silhouette = 0.
- Measured after: all bbox x 48.8-701.2, y 193.2-857.2, mid y 525.2, alpha centroid (378.7, 525.2); lowest figure ink 712.2 -> 49.8 above rule 762; bird+crown centroid x 375.2; wire ends 52/698 at y 525 (symmetric about 375).
- Review images: build/review/corr-JOKER_BLACK-{after-750,before-after,crown-3x,crown-3x-before-after,crown-6x,188-before-after-white}.png
- Status: DONE.

## ROUND 2 — iter 3 (verifier findings: no real interlace; crown slid 24 px down the bill; tip a detached sliver; gape opened; crown lost PL.clean closing)
- Fool parity target (corr-JOKER_RED iter 3): lowest figure ink 712.0 (gap 50.0 to rule 762), block middle 523.0.
- Geometry finding: a 4.2-gapped bill-OVER-band crossing cannot be placed anywhere on this crown without cutting a point or a jewel's gold surround:
  jewels at x -15/0/15 (+-4.4, +3 gold) + plain points at the ends leave only a ~4.6 px column at each band end; a crossing needs tip + 2 x 4.2 >= 10 px.
  A bill-UNDER crossing hides the tip (or leaves a detached sliver). -> use the client's alternative: the tip just catching the rim (a T-contact, ink over gold trap, as the bulb necks), crown hung AT the tip.
- Brute-force check (scratch r2/search.py): every swing -40..114 deg x every hook on the coronet -> 0 placements where a 4.2-gapped bill-over-band crossing splits the band without touching a point, finial or a jewel's 2.5-3 px gold surround.

## ROUND 2 — iter 4 (final: built + QA)
- props: COR_SWING 52 -> 64 (coronet centroid 48.2 deg off plumb, was 58.8); COR_HOOK (-24, -1) sits ON the bill tip (COR_HOOK_S and coronet_hull removed): the tip's point lies ~1.6 px over the band's bottom rim, 3 px in from its left end (ink over gold trap, like the bulb necks). FIG_SHIFT (-8.4, 72.8).
- JOKER_BLACK.build: the bird solid is no longer cut (bill + gape identical to the original: head/bill region sym-diff 0.11 px2 = coordinate rounding; gape hole 164.0 px2, same bounds). Coronet = PL.clean(coronet, keep=coronet) -> the original 1.3 px closing finish (jewel holes 26.3/26.3/26.4 px2, 36-38 verts; orig 26.3, 36 verts).
- Output (cards/JOKER-BLACK.svg): coronet one gold piece, 3 jewels, area 1086.7; ink over coronet 1.87 px2 (tip only, x 445.3-446.4 y 193.1-197.4), 0 over points/finials/jewels; tip -> nearest point 11.4, jewel hole 5.4.
- Measured: content bbox x 48.8-701.2 y 184.5-857.2, middle y 520.9; figure y 184.5-712.0, gap 50.0 (Fool 50.0); bird+coronet centroid x 375.00; alpha centroid (378.6, 523.0); wire ends 52/698 at y 524.8; bulbs 175/560/655.
- deck.build both stocks; deck.qa JOKER_BLACK: 12 pass, 0 fail, 0 warn (10c min clear 75.01; 12 vector/raster empty).
- Review images (round 2): build/review/corr-JOKER_BLACK-{after-750,before-after,crown-3x,crown-3x-before-after (orig|round1|round2),crown-6x,tip-30x,head-750px-3x (orig|round1|round2),billtop-6x-before-after (orig|round1|round2),188-before-after-white}.png. Round-1 images kept in scratchpad r2/round1_review/.
- Status: DONE.
