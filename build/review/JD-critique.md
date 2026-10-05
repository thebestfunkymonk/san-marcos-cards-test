# J♦ · The Herald of the Road — fresh-eyes critique

Draft: v27 → final v28 (`art/JD.py`, `art/_jd_parts.py`). I looked at the card at 750 px, at 1500 px with 3× and 6× crops (face,
cap and feather roots, banner, both hands, map, the tabard chain's corners), at 188 px, on white stock, and in a strip
next to J♣, J♥, Q♦ and K♦.

## What reads (keep)

* **Silhouette and story at 188 px.** The gold trumpet runs diagonally up to the right (axis −63°, bell mouth at
  (572, 126)) with a square jade banner hanging under the bell. With the feathered red cap it reads "herald", and the
  J and ♦ are clear.
* **§H.12 must-haves.** It has the trumpet, the Lion Mark banner (60 px, `lion_clasp` approach, gold solid with an
  Aquifer contour, never a halo), and two forked scissor-tail feathers (paper vanes, a current line in each, red tips
  behind a chevron). The gaze is 3/4 right, with the pupils shifted toward the bell. The lips are closed (bow plus
  lower-lip tick). The face has 11 strokes.
* **Links to the ♦ family.**
  * The tabard edging is a §G.23 stepping-stone chain knocked out to paper, which answers the Q♦ cape.
  * The sleeves carry the K♦ ford-stone brocade.
  * The ♦ lozenge brooch and buckle each have a red stone cut into the gold.
  * The cuffs and belt are gold tooled-scroll leather (§G.31: ♦ cuffs and belts).
  * The divider is the ford band.
* **Tabard.** It is a squared, T-shaped herald's tabard, not armour: the flaps are cloth, with rounded corners and
  the chain border. The gold rowels are solids with Aquifer contours, legal on red. They sit in a half-drop cluster on
  the open chest, and each rowel is kept whole or dropped.
* **Colour.** Balance (both halves): ink 14.9, gold 8.4, red 14.6, jade 15.0, paper 47.1. Paper, jade, red and ink are
  in band. The art works on white stock.

## Weaknesses found, and what I did

1. **Brows cut by the cap band** (heal trimmed both to stubs, so the face looked blank). *Fixed:* I raised the band's
   lower edge 5 px, and both brows are now full MEDIUM arcs.
2. **The hair read as a helmet with spaniel ears.** The near bob was too round and the far lock hung below the jaw
   like a flap. *Fixed:* the bob is slimmer, laps the shoulder and has 3 current lines (`first=10`, so the terminals
   fit). The far lock is a slim strip that ends at the jaw. Both are tucked under the feather and the cap band, so
   there is no gold wedge (4c).
3. **Plain jade sleeves.** Every sibling patterns its sleeves. *Fixed:* I added a ford-stone brocade (atomic, kept
   ≥ 3.4 px above the band rule). It costs about 0.3 of jade, which the balance absorbs.
4. **Chain stones jammed on corners** (flap corners, V-neck): the raster QA 12 flagged thin red wedges. *Fixed:* no
   stone is placed where the midline turns more than 22° across a stone, so the rails turn alone. Corners also round
   at r 15.
5. **Hair/collar/tabard junction.** Near-parallel outlines met at the nape (a 0.68 px QA 12 failure and an ink blob).
   *Fixed:* the bob now crosses the shoulder at a clear angle, and the neck edge is hidden under the hair.
6. **The brooch's red stone was trimmed** because it sat on the silhouette edge. *Fixed:* the brooch moved onto the
   band and is larger; the feather roots start under it.

## Remaining weaknesses (accepted)

* **Gold is 8.4 %** against the 10–15 target. The ≤ 15 hard check passes, and the family's range is 8.0–10.4. The
  brief's gold on the J♦ is thin by nature: trumpet, rowels and Lion Mark. The rowel field is small because the
  chest is crowded (chain edging, trumpet with halo, map, belt), so only 7 rowels fit whole. I added the gold cap band,
  belt and map rollers. Bigger gains would mean flat gold outside §C.1's list.
* **Tabard pattern density.** Only 7 rowels show. The half-drop reads as a cluster rather than an all-over grid.
* **Map scroll.** At 1× the route is only 2 + 2 dots either side of the river. It reads as "a map with a river and a
  road", but it is small.
* **Face.** It is kit-standard and a little blank, like J♣'s. The raised lids and pupils give the up-right gaze, but
  there is no stronger expression.
* **Cap junction (fixed after the critique).** The far lock now rises to meet the cap band, which closed the last
  QA 12 raster gap. The final `deck.qa JD` reports 14 checks passed, 0 failed and 0 warnings.
* The banner rod lies in front of the trumpet at the bell knop and the banner hangs in front of the tube. This is a
  heraldic simplification. It is not a physical lashing.
