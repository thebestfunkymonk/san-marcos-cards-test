# Aces — fresh-eyes art critique (job: aces)

Looked at: 750 px (Limestone + white), 1500 px with 3–4× crops of every emblem,
188 px row, QA flags. Baseline = the art/ modules as found (2026-09-23 23:48).

## Family (all four)

- The family reads: one pip per card on the §F.3 ace grid, gold FINE keyline on
  ♥ ♣ ♦, one gold device outside, the gold two-line caption; the A♠ is the
  showpiece with its emblem inside and the four-line legend. Keep all of that.
- Weight balance of the gold devices is uneven: the A♣ wreath is the heaviest
  gold outside any pip (long splayed blades, big node rings), the A♦ river the
  lightest. Target: wreath ≈ ripples ≈ river in visual weight.
- At 188 px the three sibling pips read cleanly by silhouette. The A♣'s interior
  reads as a *face* (two crescent "eyes" with lash-like hatching under
  "eyebrow" branches) — the only pip whose interior fights its silhouette.

## A♣ · The Reed — needs a rework (worst of the four)

1. **The spray is crude.** Four big nested arcs dominate: two 17 px-wide
   crescent leaves that parallel the side lobes' rims, and two long male
   branches that sweep the full width of each lobe above them. Parallel
   concentric arcs = eyebrows over eyes; the hatch bars on the crescents read
   as eyelashes. Nothing about it says *grass*.
2. **Male florets** hang at even spacing from a single long arc per side, like
   bunting or a mobile. Botanically the male part is several short spreading
   branches, each with 2–3 small pendulous florets on fine pedicels, smaller
   than the female spikelets and awnless.
3. **Female top** is a herringbone of six big spikelets on 50° pedicels: a
   wheat ear / fishbone. §G.5 wants *erect* spikelets close to the axis
   (pedicels short, spikelets ±15° off the axis) with one awn each — a slender
   brush.
4. **Leaves** should be §G.4 ribbons (S midrib of two tangent arcs, L:W
   10–14:1, half-hatched perpendicular to the midrib) sweeping out from the
   stem base. The current blades are ~9:1 crescents, bent round the lobes
   instead of streaming.
5. **Wreath** (§G.6): the stem is chopped by a node ellipse at every station,
   the blades splay at 24–28° with long un-hatched outlines, only three
   pairs, so it reads as three separate sprigs rather than one wreath. It
   needs one continuous arc stem, tangential leaf pairs every 14° shrinking
   6 %, a flowering spike at each tip and the reed-node knot — i.e. the same
   construction as the tuck-front wreath (deck.motifs.rice), so the family
   matches. Raster QA also flags thin gold slivers and narrow gold gaps
   inside the blade overlaps.

## A♠ · The Lion of the Source — good bones, must fix QA and two readings

1. **QA 12 fails** (after the qa.py update): ~40 gold/gold near-misses of
   0.3–2.9 px — hatch ends of one feather stopping just short of the next
   feather's outline, the paws' soles 0.9 px above the vent's top ring, the
   nose pad 0.7 px above the lip, brow ends grazing mane cusps. Every joint
   must either truly join or open to ≥ 3 px (≥ 4.2 when parallel).
2. **Wings.** The leading primary (P1) is a separate hatched strap that starts
   at the *bottom* of the lobe and runs up the spade edge to the apex: it
   reads as a rope or bandolier, not as a feather, and the two straps make a
   gable roof over the head. The wing must visibly rise from behind the mane:
   the arm should leave the mane high on the shoulder and sweep up along the
   upper edge, with the primaries hanging from it into the lobes.
3. **Face / nobility.** The level brows run straight into the nose bridge and
   the muzzle strokes hang down from the nose like a moustache: a stern man,
   not a lion. A lion reads through a broad nose bridge, a wide triangular nose
   pad, a split upper lip (ω) over a small chin, and calm almond eyes set
   under a brow ridge.
4. **Legend arc** is correct: it sags (concave up), R 600, lowest baseline at
   y 735, centred on ink; tracking and cap heights match §H.13. No change.
5. Vent / conduit / plinth: the story reads (rock → conduit → vent → lion). OK.

## A♥ · The Fount — one fix

1. **The rosette reads as a wheel/dartboard**: hub dot inside a ring, eight
   spokes to a second ring, a ring of solid dots. The Source Rosette's
   signature (back, tuck) is the crater's rib iris, the ripple rings and the
   ring of *outlined* bubbles. Rebuild at r 40 with straight ribs (§H.14):
   free hub, ribs that do not touch it, one ripple ring, outlined bubbles.
2. The pool contour's U round the vent and the rising bubble column read well;
   ripples under the point read as a surface. Keep.

## A♦ · The Ford — fine, polish only

1. The compass has no arrowheads, no N, no fleur: it reads as a rose, not a
   map pin (§H.16 must-avoid met). The half-hatch turns clockwise on all
   eight points — correct.
2. Polish candidates: the hatch dashes near the long points' tips go down to
   6 px stubs that read as dots at 188; river terminal nodes fine.

## Order of work

A♣ (spray, then wreath) → A♠ (gaps, then wings/face) → A♥ rosette → A♦ polish →
family pass at 188 → deck.build both stocks → deck.qa.

---

## Outcomes (after the fix passes; re-looked at 750 / 1500 + 3–8× / 188 / white)

**A♣** — rebuilt as a tall lyre (§H.15): culm from the upper strata line into
the top lobe, ending in a slender ERECT female brush (terminal + 2 alternating
pairs, awned); two §G.4 ribbon leaves (lit half solid paper, shaded half =
edge line + perpendicular bars, 140 × 14) rise from sheaths clasping the culm
and frame it; the male branches pass behind the leaves (roots hidden — the
visible stub read as an arrowhead on the culm) and droop into the side lobes.
Fresh-eyes pass: the florets still read as comb teeth (six plumb 10.5 × 3.7
drops at even spacing) → now four + a terminal, 14 × 4.8 (3 : 1), hung 70–84°
(≈ §G.5's ±150° off the culm axis) on alternating 11 / 8 px pedicels: they
dangle. Wreath = the deck's §G.6 construction (deck.motifs.rice, as on the
tuck): one continuous arc stem per side, pairs every 14° shrinking 6 %, a
flowering spike at each tip, the reed-node knot at 6 o'clock; fixed the stem
being cut 6 px short of its own spike (now continuous into the stalk).
Rejected: two male branches per side (candelabra tree), branches in front of
the leaves (bites out of the blades, a moustache), 66–96 px wreath leaves
(overrun the tip spikes, hatch crumbs).

**A♠** — wings are §G.2 sickles: leading edge leaves the shoulder behind the
mane, turns up through an elbow onto the spade's upper edge and curls in over
the head, its tip tucked behind the mane crown; 3 covert rows inside, 5
half-hatched primaries fanning into the lobes. Face redone (brow into a long
nose bridge, slanted almond eyes, wide nose pad, ω mouth). Retry found a QA-12
regression: the inner covert rows were raw normal offsets of the sickle and
folded into swallowtail loops at the elbow/curl → rows are now true inner
offsets, filleted (r 14), so they turn the elbow cleanly. Legend arc: sagging,
R 600, lowest baseline 735 — unchanged, correct.

**A♥** — rosette rebuilt: free hub dot, 8 straight ribs running in from the
crater rim and stopping short of the hub (an iris), ring of OUTLINED bubbles,
the pool contour's U as the outer rule. No longer a dartboard; still a little
wheel-like at 750 (see weaknesses).

**A♦** — no arrows, no N, no fleur. Hatch stubs at the tips: HATCH_MIN 6 → 10
removes the red "pill" left beside each long point's tip; the hatching now
stops short of the tip as an engraver's would.

## Remaining weaknesses

- A♥: at r 40 with MEDIUM knockout lines there is no room for both a ripple
  ring and outlined bubbles, and §H.14 asks for straight (untwisted) ribs, so
  the rosette keeps a faint "wheel" reading at 750 px; at 188 it reads as a
  rosette.
- A♣: the §G.6 paired-leaf wreath inevitably echoes a laurel at 188 px; the
  reed-node knot is small and reads as a bead with two ties. Lower halves of
  the side lobes are left as plain ink (deliberate negative space).
- A♠: the covert rows are small scallops (≈ 10 px pitch) and read as ruffled
  texture rather than individual feathers at 750; the curl tips meeting over
  the crown give the wing tops a heart-shaped outline.
- Raster QA-12 warnings (no vector failures): A♠ vent-ellipse ends and
  ear/mane acute junctions; A♣ wreath leaf-base wedges. Checked by eye at 8×:
  acute joins, not near-misses.
