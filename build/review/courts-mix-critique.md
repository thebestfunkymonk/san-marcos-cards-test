# courts-mix: fresh-eyes critique of J♣, K♥ and Q♥

I compared each card with the approved K♠ (`build/png/KS.png`) and the rest of the court family (QS JS KC QC KD QD JD JH). I looked at 750 px, 1500 px with 4× crops of the face and attributes, 188 px, and white stock. Each item is ranked by how much it hurts the card at 1×. Items marked **fixed** were changed in this pass. Items marked **open** remain.

## Q♥ · The Aquamaid Queen (§H.5)

1. **The cap did not read as a petal cap. (fixed)** At 1× it read as a knit beanie or a helmet. The petals were projected onto a sphere, and their outlines merged into zig-zags and loose hatch ticks. The silhouette was a smooth dome, and a smooth dome reads as a helmet whatever is drawn inside it.
   - The new cap is a flat rosette. It has nine petals in the deck's vesica leaf shape, radiating from a gold pearl (Ø22 with a paper highlight). Each petal has a FINE midrib, and the same half of every petal is hatched (§B.2).
   - The petals overlap pinwheel-fashion, so every petal shows its full hatched half.
   - The petal tips scallop the silhouette all round. At 1× and at 188 px the cap now reads as a 1950s petal swim cap.
   - The gold band lies in front of the petals, which tuck under it. This gives a clean forehead line and no petal-over-band slivers.
2. **Hidden plates under the ink (4c). (fixed)**
   - Jade under the ink at the cap: fixed by the band-in-front construction. The jade base is inset under the petals and clipped to their hull, and the band now ends square at x 418 instead of tapering.
   - Jade and gold under the ink at the arrowhead leaf: the jade fill now stops 3.3 px short of the sharp lobe tips. The notch between the lobes is opened to 13 × 22, and the petiole is slimmed to 7 px so its gold no longer wedges into the sinus.
   - QA 4c is now ✓.
3. **Gold is 8.4 % against a 10–15 target. (open)** The hair, pearls, band, flower centre and stem carry the gold. Raising it would mean more gold hair or a heavier band, and the card reads well as it is.
4. **The near-side hair flip swings out to x ≈ 214. (open, deliberate)** It reads as hair floating underwater, which suits an Aquamaid. It is the most unusual silhouette in the family.
5. **The cap is taller and fuller than the other queens' headwear. (accepted)** That volume is what makes it read as a petal cap and not a helmet.

## K♥ · The Ferryman King (§H.4)

1. **The glass-bottom window scene (the card-within-a-card). (fixed)** Before this pass:
   - The two eelgrass ribbons were paper outline pairs, and at 1× they read as a pair of prongs.
   - The vent boil was three whole concentric rings, which read as a target.

   Now:
   - The eelgrass is two solid paper blades (the card back's knockout language) that rise from the bed and sway right with the current.
   - The boil is three flat rings rising into view from the bed at the right (§G.8), so it reads as a boil on the lake floor.
   - The darter, with its fins and stitch line, is unchanged.
2. **The punting pole was a plain gold rod. (fixed)** `_kh_parts.pole()` gains a spiral cord grip wrap: MEDIUM turns 8 px apart, each slanting 7 px along the shaft, just above the fist (y 378–426). The pole keeps its cord bindings near the top and at the shoulder. It now reads as a made pole, next to the K♠'s segmented sceptre. The pole still passes behind the head and crown and is cropped by the frame at x ≈ 275.
3. **Earlier slivers. (fixed in the earlier pass, confirmed)**
   - The 4c red-under-ink at the left robe edge is gone.
   - The ripple knockouts stop 5.6 px above the band.
   - The chalice's ship's-wheel vent is now a §G.1 crater.
4. **Jade is 14.7 % against a 15–20 target, and paper is 45.1 %, at the bottom of its band. (open)** Widening the lapels by 4 px bought only +0.1 jade and cost +0.3 ink, so I reverted it. The card sits at the edge of the targets without breaking any hard check.
5. **Twelve raster 12 warnings. (open, accepted)** All are acute wedges: the scale lattice running into outlines, the window frame against the lapel edge, and hair current lines running into the contour. I cropped each one at 8× and confirmed it.

## J♣ · The River Squire (§H.9)

1. **The face and its youthfulness. (fixed in the earlier pass, re-checked)** The face is now the kit's 3/4-left `age='young'` face with raised lids and the pupils thrown 3 px downstream. That is the J♦'s hand, mirrored: side by side at 4× the two jacks are clearly one family. The far eye joins the contour. The earlier QA 12 vector failure (pupil 2.85 px) is gone.
2. **Colour balance was the thinnest in the family: gold 7.0, jade 13.3. (improved)**
   - The near-side bob is fuller (outer edge +6 px) and so is the far lock (+5 px): gold 7.0 → 7.6.
   - The left puffed sleeve is 6 px fuller: jade 13.3 → 13.7.
   - Paper went from 49.6 to 48.6.
   - Gold is still the lowest in the family; the next lowest is J♠ at 7.5.
3. **The cap hatband had a 4c jade-under-gold plate. (fixed in the earlier pass)** The jade cut under the band now opens through the contour.
4. **The jerkin is boxy. (open)** It has straight vertical sides at x 244 and 536 and reads as a red rectangle beside the family's curved mantles. Tapering it would mean re-fitting the gold braid guards, the belt and the pecan-leaf field, which is a redesign rather than polish.
5. **The belt hand is small and flat. (open, minor)** It reads correctly as a hand resting on the belt.

## QA (deck.qa, both stocks)

JC, KH and QH are ✓ on every hard check (1, 4, 4b, 4c, 5, 5r, 6, 8, 10a, 10c, 12 vector, 17, 24, 25). KH and QH carry only 12-raster acute-wedge warnings.
