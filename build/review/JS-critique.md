# J♠ · The Lantern Page — critique (fresh eyes, against K♠, J♥, J♣)

State reviewed: the interrupted draft after the one-line repair (`hg.outer` → `hg.shape`),
rendered 750 / 1500 / 3× / 188 / white. QA: 5r ✗, 4c ✗, 12 ✗ (2.92 px),
balance paper 57.0 / jade 12.0 / red 9.7 / gold 6.1 (all four off target).

## What the family does that this card does not

The finished courts (K♠, J♥, J♣) share one read at arm's length: a head at the kit
size with a clear paper face, headwear that sits ON the head, a wide bust that fills
the window from ~x 150 to ~x 600 (paper ≈ 45–50 %), arms that read as arms (sleeve →
cuff → mitten), and one or two big attributes with a simple silhouette. The J♠ draft
misses on nearly every one of those.

## Head and face

1. **The hood swallows the head.** The red mass runs from the crest (y ≈ 128) to the
   cape with no neck or shoulder break — a diving-suit / "sock" silhouette. The face
   opening is only ~60 × 95 px and sits at the extreme right edge of the hood, so the
   paper face reads as a slot, not a portrait. J♥'s face (same kit, same r 42.5) reads
   twice as large because the beret sits above the brow and the bob is behind the ear.
2. **Hood construction.** The rim runs almost vertically from brim to jaw, so the hood
   has no temple / cheek shape; it also wraps the chin with a jade band that looks like
   a chin-strap. The back of the hood is a straight vertical wall to the cape.
3. **Crest.** The stepped crest is a boxy red slab with a paper pipe line; it reads as a
   cap badge or a folded paper crown, not as three fault-steps (the steps are ~8 px and
   vanish at 188). It also sits behind the brim so the front of the head is flat-topped.
4. **Face drawing.** Profile construction is sound (G1 chain), but the nose is short and
   blunt, the mouth line is a short dash, and the eye/brow sit high and small against the
   lining. The lock of hair is a thin gold crescent pressed between lining and face; it
   reads as a strap, not hair. "Gold hair locks escape the hood" is not legible.
5. **Lion Mark badge** floats on an empty red cheek of the hood with no anchoring seam.

## Body

6. **Slab torso.** `torso()` with plumb sides and a 40 px corner makes a box; the cape
   is a flat-bottomed band over it with a row of small zigzag dags + dots (reads as a
   sweater yoke / jester collar at 188 px).
7. **Doublet pattern.** Full-width MEDIUM knockout chevrons with four faults read as a
   knitted jumper; the fault never reads because there are four of them. Nothing on the
   doublet is plain, so there is nowhere for the eye to rest (the K♠ has a 54 px plain
   border; J♣ keeps its jade panels calm).
8. **Belt** is fine in idea (gold, karst rings) but it is a flat strip 34 px tall across
   the whole body with a big buckle; with the band 11 px below, the waist is crowded.

## Arms, hands, attributes

9. **Lantern arm is unreadable.** Fist at head height (516, 234) with the wrist 50 px to
   the right and a narrow jade tube dropping to an elbow at the frame edge: the hand
   looks broken at the wrist, the arm looks like a drainpipe beside the lantern. 4c
   warnings and a 5r come from the cuff / chain tangle there.
10. **Salamander cap reads as a cog / horseshoe.** Radial limbs and toes stick out like
    gear teeth; the head is a stub. Nobody would read "coiled salamander".
11. **Lantern body** is decent (four posts, rails, rays, vesica flame, drip) but the burner
    cup and flame are too small in a big pane, the rays in the side panes are cramped,
    and the gold posts + rails read heavy relative to the panes.
12. **Rope coil** is a flat paper ring on the chest (the top passes behind the cape, so it
    does not read as slung OVER the shoulder); the fist gripping it is a large white
    block with the wrist hidden. Two strands at 13 px read as a ring, not a coil.

## Colour balance / QA

13. Paper 57 % (figure too narrow and too small), jade 12, red 9.7, gold 6.1. The lantern
    and belt are the only gold; locks and salamander add almost nothing.
14. QA: 5r thin gold on red at the chain/salamander (504–520, 300); 4c jade and red under
    the ink solid (fist / cuff at 586, 389 and 505, 297); 12 vector 2.92 px at (260, 339)
    (coil vs cape).

## Plan

* Rebuild the hood as a proper chaperon hood: skull + 12, a face opening that starts
  above the brow and curves round the cheek in front of the (covered) ear to under the
  jaw, a jade lining band; a clear three-step crest on the crown (≥ 12 px steps) that
  reads at 188; a short cape over the shoulders with a few large stalactite dags.
* Face at kit size, re-pinned profile (longer straight nose, fuller mouth, a real
  raised lid); gold locks as a fringe under the brim and a lock curling at the cheek.
* Wide bust: cape spanning ~x 180–570; shaped doublet with sleeves; a plain border and
  a calmer chevron field with ONE centre-front fault.
* Lantern arm: the JH construction (fist on the chain above the lantern, forearm behind
  the lantern, elbow and sleeve visible below-right); salamander redrawn as a legible
  coiled cast (broad head, eyes, legs along the body, tapering tail) forming the bail.
* Rope coil: a tilted bundle lying over the viewer's-left shoulder (on top of the cape),
  three strands with helix ticks, gripped by the left fist.
* Then balance (paper ↓, jade/red/gold ↑) and QA.

---

## Resolution (final state, cards/JS.svg · build/png/JS.png)

| # | issue | what was done |
|---|---|---|
| 1–2 | hood swallows the head; no temple / cheek shape; chin-strap | Hood rebuilt from explicit G1 spline runs: skull + 13, rim from the brow back over the temple, down in front of the covered ear, round the jaw and under the chin; lining 12 px, stopping short of the brim point. The face opening is now ~70 × 115 px; the neck shows under the chin. |
| 3 | crest reads as a slab / cap badge | Jade comb of three level treads and plumb risers (139 / 126 / 113, 13 px steps) rising to the back, one fall to the dome, middle course hatched like the strata; convex corners softened (clears 4c). |
| 4 | face short-nosed, locks read as a strap | Nose 10, raised RULE lid with the pupil at the front, a visible nostril hook (new `nostril` parameter), fringe curl under the brim + side lock rolled at the cheek (tapered ribbons with curls). |
| 5 | badge floating on the hood | Lion Mark is the pendant of a gold livery collar of graduated pearls on the cape at the throat. |
| 6 | slab torso, zigzag yoke | Cape over both shoulders (x 166–596, shoulders ≈ 300) with six slender concave stalactite dags; puffed jade sleeves to the band. |
| 7 | knitted-jumper chevrons | Λ chevron rows (pitch 25) knocked out, broken by a plain placket with two gold buttons; the right half drops one course across it (the fault). |
| 8 | crowded waist | Belt 464–498, buckle 38 × 46 clear of the band rule. |
| 9 | lantern arm unreadable | Red forearm rises from the right to the fist (523, 180) holding the chain (an end loop shows above the fist); jade cuff. |
| 10 | salamander reads as a cog | Coiled salamander bail: round-snouted head raised at the left, eye, fore- and hind-leg with paddle feet, tail spiralling in; the chain's last link hooks through the ring. |
| 11 | lantern proportions | R 58 lantern: collar, hexagonal roof with hip ribs (left facets hatched), cornice, 4 posts, ray-lined panes (rays spring from the flame, butt on the frame), vesica flame with red core on a burner, two-tread plinth, hatched stalactite drip; frame lines drawn once (disjoint partition). |
| 12 | rope a flat ring | Three-turn coil with MEDIUM divisions and FINE lay ticks, staggered between turns and laid greedily (no crowding, no crossings), gripped by the left fist; red forearm and cuff. |
| 13 | balance | paper 57.0 → 49.0, jade 12.0 → 14.8, red 9.7 → 11.6, gold 6.1 → 7.5, ink 17.2 (waiver ≤ 19). |
| 14 | QA 5r / 4c / 12 | All clear except 12 raster (!): 8 narrow paper wedges (salamander legs at the collar, roof rib against its hatch, coil against a dag) — looked at, acceptable. |

**Still weaker than the best of the family:** gold stays at 7.5 % (legal gold is only
lantern, locks, belt, buttons, pearls and badge; the crest is kept jade); jade and red sit
just under their bands; the salamander's legs only read at 2–3×; the coil lies on the
cape rather than visibly passing over the shoulder line; the upper-left quadrant is
open paper (no tall attribute there, by the brief).
