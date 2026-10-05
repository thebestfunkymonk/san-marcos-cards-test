# JOKER_BLACK · The Trickster: critique of the inherited version

Reviewer: the senior artist taking over the piece (fresh eyes, before touching code).

**Inputs**
- Build: `deck.build JOKER_BLACK` (+ `--stock white`).
- QA: `deck.qa JOKER_BLACK` gives 12 pass, 0 fail, 0 warn.
- Looked at: 750, 1500 and 2250 (3× crops of head, coronet, wing, feet and wire), and 188 on Limestone and on white.
- Compared with: the sky-pointing reference (`research/refs/jokers/grackle_Great_tailed_Grackle_2_jpg.jpg`), the keel-tail side view (`…RWD`), the Monarchs joker (`monarchs_rpc_monarchs-10.jpg`) and the Drifters joker (`drifters_rpc_drifters-2.jpg`).

**Verdict**
- The machine checks are clean, but the drawing is not yet premium.
- At 188 px it reads as "a black bird on a wire". The grackle's own features (skyward bill, flat crown, keel tail) are there but under-stated.
- Up close, several parts read as diagrammatic rather than drawn: the wing, the feet, the coronet and the call rays.
- The fixes below are ordered by how much they cost the piece.

## 1. Gesture and silhouette (the biggest problem)

1. **Posture is a straight diagonal, not the display.**
   - The body leans 60° and the tail carries on along almost the same line. The whole bird is one slash from the bill down to the lower-left tail tip.
   - The sky-pointing reference is an upright S: bill vertical, neck stretched straight up, body nearly upright over the feet, and the tail dropping plumb behind the perch.
   - The diagonal reads as a bird toppling backwards. It is also the least "heraldic" gesture available: no verticality, no poise.
2. **Balance.**
   - The feet are about 40–60 px right of the body's mass. The legs strike out forward-right from under the belly like a kickstand, so the bird looks as if it is leaning back against nothing.
   - A perched bird's centre of mass sits over its grip.
3. **Scale.**
   - The figure is about 230 × 530 px. The y 90–640 band is used, but the figure is a thin diagonal, so the card reads empty.
   - The bird should stand taller and more frontal to the viewer, with the tail and body filling the band like the Monarchs penny-farthing figure fills its card.
4. **The keel is not stated.**
   - The tail is a flat strap of three bands with round tips. Nothing says "folded V" except its depth.
   - The first artist admitted the V's cross-section isn't drawn.
   - "Tail folded into a tall keel" is a must-have, and it needs a readable device.
5. **Head and neck are a large undifferentiated mass.**
   - The neck is as wide as the head from the eye down, so head and neck form one long cone.
   - There is no occiput and no nape turn. The flat crown doesn't read as a crown; it is just the cone's left edge.
   - The grackle's slim, stretched neck and small flat-crowned head (reference) are lost. At 188 this cone plus the bill is what reads as "crow".

## 2. Anatomy and drawing

6. **Wing.**
   - The flight feathers are long parallel bands, each a pair of paper lines with a round-capped free end at the top. They still read as a stack of tubes or fingers.
   - The covert rows are separated from the flight feathers by an arbitrary scalloped edge. The wing has no wrist, no tertials and no sense of overlap (which feather lies on which).
   - The wing tip dissolves into the tail: at 750 you cannot say where wing ends and tail begins.
7. **Breast scale arcs.**
   - A column of ")"-shaped hooks with round-capped ends marches down the breast beside the wing edge.
   - They don't form rows, don't follow the body's roundness, and read as "wormy" squiggles.
8. **Tail feathers.**
   - The right (keel) edge runs as one straight line to a needle point, while the left side has three rounded lobes. It reads lopsided.
   - Hatch direction flips between the two jade tracts ("/" on one, "\" on the other) in the same tail, which looks busy.
9. **Legs and feet.**
   - The tarsi are straight 7.2 px bars in a wide A-stance. The feet are flat plates lying on the wire with tiny claw hooks: they read as roller-skates.
   - A perching bird's toes wrap round the wire (three forward, the hallux behind) in a C-grip.
   - The legs are also a non-token uniform band (7.2 px), which is arguable against §B.2.
10. **Bill and gape.**
    - The bill is good: long, pointed, flat culmen.
    - The gape line, however, is a short free-floating paper dash in the middle of the bill with a round end. It reads as a highlight streak, not the commissure.
11. **Eye.**
    - The gold ring is right, but it is a heavy "donut" floating in the black cone.
    - It sits too far from the bill base for a grackle and too centred: the eye should sit just behind the gape, close under the crown line.

## 3. Coronet, rays, wire, bulbs

12. **Coronet (must-have) fails at 188 and is ambiguous at 750.**
    - It is small (about 40 px), rotated 52°, and cut 4.2 px clear of the bill tip.
    - As a result it floats beside the bill: nothing touches, grips or hangs. It has a nick where the interlace cut it.
    - At 188 it is a gold splat or flower. It must read unmistakably as a crown and as *hanging from the bill tip* (§H.18).
13. **Call rays.**
    - They start at a fixed distance from an irregular outline, so their inner ends are ragged and their angles look arbitrary.
    - The result reads as cartoon "shock lines", which works against the brief's "dignity, not cartoon".
    - The five rays should be a disciplined fan: equal length, equal angular pitch, all on one arc.
14. **Wire and bulbs.**
    - The bulbs are nicely drawn: socket, globe, knocked-out glint.
    - But the placement (x 175 | 560, 655) reads as random rather than deliberate: one isolated left, two bunched right.
    - The wire kink under the feet is good physics. The wire, though, is a MEDIUM line that passes behind the tail and then simply stops behind the belly, so the bird doesn't visibly *stand on* it.

## 4. Line discipline, spacing and type

15. **Free ends.** Many wing and tail knockout lines end in round-capped free ends mid-solid (§I.14 asks for no ragged ends). A better construction makes every feather edge emerge from under its neighbour (T-joins), so no line dangles.
16. **Knockout rhythm.** Line spacing inside the wing is uneven, and so is the scale size on the breast. Nothing graduates (small to large) the way real feather tracts do.
17. **Jade.**
    - About 12 % of the bird, which is right. The shoulder patch is the right idea (brightest gloss), but its window is an arbitrary lozenge, and it reads as a striped sticker.
    - The tail windows are narrow slivers.
    - "Alternate tracts" should read as a system: coverts / flight feathers / tail.
18. **Type.**
    - Title and subline are verbatim (§J.2) and in the right faces, caps, tracking and baselines.
    - The subline counters workaround is correct and passes QA.
    - No issue here, except that JOKER_RED will hit the same counter problem (a system note, not ours).

## 5. Brief compliance summary

| Item | State |
|---|---|
| Skyward bill | yes (76°); could be steeper, closer to the reference |
| Keel tail | weak: deep tail, but no V device |
| Gold eye ring + Aquifer pupil | yes, heavy |
| Stolen coronet hanging from bill tip | **no**: floats beside the tip, unreadable at 188 |
| Festoon wire + 3 gold bulbs | yes; spacing reads random |
| Aquifer silhouette, scale arcs knocked out | yes; scale arcs are wormy |
| Alternate tracts half-hatched jade | partly; windows arbitrary |
| Five FINE dash rays | yes; irregular, cartoonish |
| Caption verbatim | yes |
| Not crow/raven | borderline at 188 (thick head/neck cone, diagonal posture) |
| No gradients/trash/mockery | yes |
| §I.1–4, 8, 12, 17, 24, 25 | pass (QA) |
| §I.14 line ends | many round-capped free ends in knockouts |
| §I.18 style fidelity | not yet: diagrammatic wing and feet |

## 6. Plan

1. Re-draft the pose from the sky-pointing reference: an upright S, bill near-vertical, slim stretched neck, small flat-crowned head, body over the feet, and a long tail hanging nearly plumb, filling y 92–638.
2. Rebuild the plumage as **stacked feather shapes with occlusion**, so every knockout line is the visible edge of a feather emerging from under its neighbour (T-joins, no free ends):
   - covert scale rows graduating in size;
   - tertials;
   - primaries projecting in steps to a clear wing point that lies on the tail;
   - breast scale rows that follow the body's roundness.
3. The keel: show the V by drawing the far vane of the folded tail rising behind the near vane along the dorsal edge. That makes two planes meeting at the keel line, with the graduated tips stepping down to the long central pair.
4. Jade as a system:
   - the gloss tracts (lesser coverts on the shoulder, the greater-covert row, the inside of the tail's V) are half-hatched;
   - the flight feathers and near tail vane stay black;
   - one hatch angle per tract, consistent.
5. Coronet: a clearly readable open coronet (band + points + pearls), about 50 px, **gripped in the bill tip by its band** and hanging below it (the tip overlaps the band: the bill is in front, interlaced), with a slight swing.
6. Feet: toes wrapping the wire (three forward, hallux behind) under the body's centre. Tarsi drawn as legal-width forms.
7. Call rays: five equal FINE dashes on one arc, at an even angular pitch, fanned behind the crown.
8. Wire and bulbs: an even bulb rhythm read as deliberate. Re-balance against the new silhouette.
