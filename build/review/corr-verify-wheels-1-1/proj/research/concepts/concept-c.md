# ENDEMICS

**Concept C · "Natural Heraldry"**

**Tagline:** *A royal court found nowhere else on Earth.*

**Mottos** (original Latin, written for this deck):
- **NUSQUAM ALIBI**: "nowhere else". Used on the seal and the tuck ribbon.
- **FONS NUMQUAM DEFICIT**: "the spring never fails". Used on the Ace of Spades and a tuck side.

**Sources and conventions:**
- Facts come from `research/san-marcos.md` (cited as §) and style rules from `research/style.md` (cited as "rule n").
- All sizes are in px on a **750×1050 card**: poker trim at 300 dpi, so 1 pt = 4.17 px.

---

## 1. Narrative

San Marcos sits on the Balcones fault. There the Edwards Aquifer surfaces through more than 200 spring openings. The water is 72 °F all year, and the springs have never been known to stop. Around them lives a kingdom of rarities: a salamander that sees without eyes, a wild rice found only in the river's upper few kilometres, and a darter shorter than a thumb. ENDEMICS crowns them.

Each suit is a realm on the water's journey. The water rises from THE DEEP (♠), runs as THE CURRENT (♦) and feeds THE GROVE (♣). It falls as rain on THE HILL (♥), then sinks home. Every court is a natural-history plate made royal, with its Latin name set across the divider like a specimen label. The Ace of Spades is the Source itself. The jokers are the court's two outsiders: a grackle that arrived around 1900, and a pig that dove in anyway.

---

## 2. Design stance

**The line.** Monoline geometric line art, not burin engraving (style §0).
- The "botanical-engraving" elegance comes from plate conventions: specimen captions, precise arc-and-line construction, dense even hatching and restraint.
- Swelling lines are not used.
- Half-hatching is the only tone device (rule 3).
- Every free line end becomes a **bubble** (rule 9, localized).

**The heraldic engine.** The deck invents its own blazon:
- four new **lines of partition**, one per realm: *fault-step*, *ripple*, *cypress-knee*, *petal-engrail*;
- one new heraldic fur: *bobcat-spot ermine*.

The partition lines draw every court divider, ace mount and tuck roundel. As a result the suit can be read from the ornament alone.

**The courts** are custom, 180°-rotational half-figures (rule 19b). They keep the traditional cues players know:
- one-eyed profiles on J♠, J♥ and K♦;
- K♥'s blade behind the head;
- K♣'s orb, K♠'s upright staff and K♦'s blade;
- queens holding flowers.

**Clearances from Jinkins' signatures** (style §10, motif bible §7). The deck has none of the following:
- no creature pair twisting on a vertical axis;
- no Latin edge-mottos;
- no stepped Deco corners with dot rules, and no piano keys;
- no diagonal title band, shield-with-arrows or coin seals;
- no crown inside the spade;
- no penny-farthing and no sawtooth medallion;
- no serpentine river spine.

---

## 3. Palette

| Token | Hex | Role |
|---|---|---|
| **Limestone** (paper) | `#F4EEE0` | Face stock: ivory, like herbarium paper. Print on a natural/ivory stock. If only bright white is offered, use `#FFFFFF` and change nothing else. |
| **Aquifer** (ink 1, key) | `#16232B` | Blue-black key line and all contours. Pips and indices of **♠ ♣**. The A♠ and A♣ silhouettes. |
| **Gill Red** (ink 2) | `#A8322B` | Pips and indices of **♥ ♦**. Red garment panels, salamander gills, paintbrush bracts, monarch wing cells. |
| **Spring Jade** (ink 3) | `#1F5A55` | Court garment panels, leaves, water and bluebonnets. **Card-back flood.** |
| **Cypress Gold** (metallic) | stand-in `#B08D57` | Metallic ink on faces (871-type metallic). Hot foil on the tuck. Foil preview gradient `#8A6A34 → #D8B56A → #F6E3A1`. **Line only, never a flood** (rule 14). |
| **Deep Hole** (tuck board) | `#102B2A` | Jade-black uncoated board, named for Spring Lake's "Deep Hole" vent (§1.1). |
| Cypress Russet (alt back) | `#8A4A2A` | Second-edition back flood. |

- **Suit colours:** red suits (♥ ♦) print in Gill Red; black suits (♠ ♣) print in Aquifer.
- **Card back:** Spring Jade flood with every line knocked out to paper, so one ink. Alternate editions: Cypress Russet, and Aquifer.
- **Ink budget:**
  - faces use 3 inks plus 1 metallic;
  - the back uses 1 ink;
  - the tuck uses 1 gold foil plus blind emboss on Deep Hole board (rule 13).
- **Court proportion target:** about 50 % paper, 18 % jade, 14 % red, 14 % Aquifer line and 4 % gold line.
- **Check:** swatches rendered on Limestone confirm that Aquifer reads as black next to Gill Red, and that gold line holds on Deep Hole.

---

## 4. Typography

The deck uses two families only: **Cinzel** (inscriptional Roman capitals, the voice of plate captions) and **Playfair Display SC Black** (the Didone of 19th-century natural-history title pages). None of the supplied fonts has an italic. Latin names therefore follow the plate-label convention of tracked capitals.

| Role | Font | Setting | Size on 750×1050 |
|---|---|---|---|
| **Rank index** | `Cinzel[wght].ttf` @ wght 700, converted to outlines | Horizontal scale **0.80** (measured: K is 79 px wide, "10" is 103 px wide). "10" is tracked −8 px. **Q** tail redrawn as a short flick (≤12 px below baseline, ≤8 px past the bowl). **J** redrawn with a shallow hook (≤12 px below baseline). | Cap height **90 px (0.30 in)**, so font-size 128.6 px. Rank axis x = 88. Cap top y = 44, baseline y = 134. The "10" spans x 37–140, so the inset is ≥0.12 in. |
| **Index pip** | Custom suit paths | Solid, no ornament | 66 px wide, top at y = 156, same on all 54 cards. The bottom-right copy is rotated 180° about (375, 525). |
| **Joker index** | Cinzel 700, x-scale 0.80 | "JOKER" stacked vertically | Cap 44 px (font-size 63 px), leading 54 px, axis x = 80 |
| **Wordmark "ENDEMICS"** | `PlayfairDisplaySC-Black.ttf`, outlined | Tracking +60. **0.5 pt inline**: an inward offset of the glyph outline by 30 % of stem width, stroked in paper or stock. **Hatched shadow**: 45° hatch at 0.5 pt, offset 5 px down-right, clipped to the shadow shape. It is an engraver's shadow, deliberately not Monarchs' chamfered sans with a solid drop shadow. | Tuck: cap 72 px (front 769 px wide). A♠: cap 40 px. |
| **Captions, legends, mottos** | Cinzel wght 600, all caps | Tracking +180; flanked by 0.5 pt em-dash rules 24 px long | **4.5 pt = 18.75 px** by default (court captions, ace legends, plate labels). **4 pt = 16.7 px** is the minimum. |
| **Joker titles, tuck subline** | Cinzel 700 | Tracking +250 | 7 pt = 29 px (joker title); 6 pt = 25 px (tuck subline) |

Measured check: the longest court caption, "SETOPHAGA CHRYSOPARIA" at 4.5 pt with +180 tracking, is about 340 px. That fits inside the 430 px inner frame.

---

## 5. Suits, partition lines and pips

| Suit | Realm (plate label) | King · Queen · Jack | Partition line |
|---|---|---|---|
| ♠ Aquifer | **THE DEEP · PROFUNDUM**: Edwards Aquifer, caves, Balcones fault (§1.3–1.4) | Aquifer King · Blind Queen (*Eurycea rathbuni*) · Salamander Page (*E. nana*) | **Fault-step** |
| ♦ Gill Red | **THE CURRENT · FLUMEN**: the spring-fed river (§1.2, §2.1, §2.4, §2.18) | Kingfisher King · Wild-Rice Queen · Darter Knave | **Ripple** |
| ♣ Aquifer | **THE GROVE · NEMUS**: cypress and pecan banks (§2.7–2.8, §2.13) | Cypress King · Pecan Queen · Bobcat Knave | **Cypress-knee arcade** |
| ♥ Gill Red | **THE HILL · COLLIS**: the Hill Country above the fault, with juniper-oak woods, bluebonnet prairie and the fall flyway (§2.10, §2.11, §2.19) | Warbler King · Bluebonnet Queen · Monarch Herald | **Petal-engrail** |

**Rank logic.**
- The King is each realm's elder or ruler.
- The Queen is its grace: a plant or, in the lightless Deep where nothing grows, the oracle salamander.
- The Jack is its quick messenger creature.

**Order.** The plates follow the water: I PROFUNDUM → II FLUMEN → III NEMUS → IV COLLIS, then back underground.

**Pip styling.** Playability comes first: standard Bicycle-proportioned silhouettes in solid ink.
- **Index pips** are plain solid.
- **Field pips** (2–10, 118 px wide, about 128 px tall) carry one hairline "plate mark": a 0.5 pt paper inline set 6 px inside the edge. At arm's length the pip reads solid; up close it reads engraved.
- **♠ and ♣ stems** flare at the foot in a concave **buttress** curve, like the base of a cypress trunk. The foot is 0.42× the pip width, with flare arcs of radius 0.35× the pip width.
- **♦ sides** are very slightly concave (a sagitta of 3 % of the side length).
- **♥** is standard, with lobes drawn as true circles.
- There are no pictures inside field pips; the pictures live on the aces.

**Layout.** Standard USPCC positions:
- side columns at x = 220 and 530, centre column at x = 375;
- outer pip rows centred at y = 205 and 845.

A mock-up confirms the field pips clear the "10" index column by ≥40 px at the top-left and ≥20 px at the rotated bottom-right.

---

## 6. Court template (shared by all 12)

**Frame**
- Outer rule: 1.0 pt Aquifer, x 144–606 × y 44–1006.
- Inner rule: 0.5 pt gold, 6 px inside the outer rule.
- **Chamfered corners**: 16 px at 45°. Each cut-off corner holds a **bubble string** of three circles (6, 4 and 3 px, 0.5 pt) rising toward the card corner. This avoids both Drifters' notch-and-dot corners and Monarchs' concave coves.

**In-frame pip.** 64 px, top-left inside the frame at (162, 62), plus a rotated copy at bottom-right.

**Specimen band (the divider)**
- A horizontal band at y 489–561, bounded by 0.5 pt Aquifer rules.
- **Centre:** the suit's partition line, amplitude ≤9 px.
- **Above the line:** the upper figure's Latin caption, upright and centred (cap top about y 497, baseline about y 510).
- **Below the line:** the same caption rotated 180°, so it reads upright when the card is turned.
- Each caption is flanked by em-dash rules that end in the court's own **glyph** (named in each brief).

**Rank grading on the partition line**
- **Kings:** a doubled line (two copies 6 px apart).
- **Queens:** a single line with a 3 px bead in each trough.
- **Jacks:** a single plain line.

**Figure**
- Draw the upper half in local coordinates, 462 × 445, then rotate 180° about (375, 525) to make the lower half.
- Line weights, 2:1: contour 1.5 pt (6.25 px), interior 0.75 pt (3.1 px), hatch 0.5 pt (2.1 px) at a 7 px pitch.
- Faces are geometric and left as paper:
  - head: an egg-oval about 88 × 112 px;
  - eyes: vesicas 22 × 9 px with 5 px pupils;
  - brows: arcs;
  - nose: one line plus a small hook;
  - mouth: two arcs.
- Hair is parallel ribbons, with every other ribbon half-hatched.

**Colour**
- Flat Gill Red and Spring Jade garment panels are allowed, up to 35 % of the figure. Patterns on them are knocked out to paper or drawn in Aquifer.
- Gold is line only: crowns, jewels and attributes.
- Every court uses the full palette regardless of suit, as standard courts do.

**Care rules** (§6)
- No court handles a living endangered species. Plants appear only as crowns, garments or crafted gold scepters, never as picked specimens.
- No court holds an animal.

---

## 7. Court briefs

### ♠ THE DEEP

**K♠, The Aquifer King** · `EDWARDS GROUP · CRETACEOUS`
- **Who:** the Edwards limestone and its hidden water.
- **Gaze:** the only frontal king, eyes level under heavy lids.
- **Crown:** limestone blocks stepping down left-to-right in three tiers (the Balcones step), bedded with hatch, with a gold vent rosette at the brow.
- **Beard:** squared, of vertical lines (rain recharging through rock), breaking into ripple arcs at the band.
- **Robe:** strata bands (plain / hatched / *karst honeycomb*), jogged one band down along a diagonal fault.
- **Holds:** a gold **karst orb** in section (strata, three water-filled voids) and an upright stone-drum staff crowned with a vent rosette.
- **Colour:** jade strata, gold crown, red collar lining.
- **Glyph:** hex void. **Divider:** doubled fault-step.

**Q♠, The Blind Queen** · `EURYCEA RATHBUNI`
- **Who:** the Texas blind salamander, oracle of the caves beneath the city (§2.2).
- **Gaze:** 3/4 left, head tipped down, listening. The eyes are closed arcs with a 3 px dot under each (vestigial eyes under the skin).
- **Headwear:** a gold circlet hung with nine **stalactite** points over a pale veil.
- **Collar:** a standing ruff of **red feathery gills**, three plumes per side; the loudest red in spades.
- **Gown:** mostly paper, with sparse contour lines, a dotted side seam and spindly sleeves.
- **Holds:** a jade finned stole (the tail) and a round fan whose face is a vent rosette.
- **Glyph:** two dots. **Divider:** beaded fault-step.

**J♠, The Salamander Page** · `EURYCEA NANA`
- **Who:** the San Marcos salamander, the dark messenger where the Deep meets the light: Spring Lake and the upper river (§2.3).
- **Gaze:** one-eyed profile facing right. The large bright eye makes him the seeing counterpart to his Queen.
- **Cap:** a skull-cap with red gill-plume cockades.
- **Doublet:** dense Aquifer half-hatch with a seam of paper dots, and a jade ripple collar.
- **Holds:** a gold cage-lantern whose flame is a tiny vent rosette (he carries light upward), and a hornwort sprig of combed whorls (§1.1).
- **Glyph:** gill plume. **Divider:** plain fault-step.

### ♦ THE CURRENT

**K♦, The Kingfisher King** · `MEGACERYLE ALCYON`
- **Who:** the belted kingfisher, one of three kingfishers hunting the River Walk (§2.18); the realm's watcher.
- **Gaze:** strict profile facing left (the traditional one-eyed K♦), with an unblinking eye on the water and a dagger-straight brow-to-nose line.
- **Crown:** the **ragged crest**, seven swept-back half-hatched plumes over a gold circlet.
- **Dress:** a paper-white collar ring, a jade breast-band belt with a gold buckle, and a scale-feather mantle with dotted wing edges.
- **Holds:** an upright dagger replacing the traditional axe, its blade hatched at 45° and its guard ending in bubbles.
- **Colour:** red lining only.
- **Glyph:** feather. **Divider:** doubled ripple.

**Q♦, The Wild-Rice Queen** · `ZIZANIA TEXANA`
- **Who:** Texas wild-rice, the deck's signature. It grows only in the upper 4–5 km of the river and was listed in 1978 (§2.1).
- **Gaze:** 3/4 right, lowered to the water.
- **Hair:** ribbons that become ribbon leaves.
- **Crown:** the plant's own flower: erect gold spikelets with awns above the band, and drooping florets below it.
- **Gown:** vertical ribbon-leaf panels with midribs, half-hatched on alternating sides and bowed by current, over a jade ripple-hemmed underdress.
- **Holds:** a crafted gold scepter with a spikelet finial, tied with a red ribbon.
- **Glyph:** spikelet. **Divider:** ripple with bubble beads.

**J♦, The Darter Knave** · `ETHEOSTOMA FONTICOLA`
- **Who:** the fountain darter, 19–30 mm, found only in the Comal and San Marcos spring systems (§2.4).
- **Gaze:** 3/4 left, youthful, with a small confident smile.
- **Cap:** a **spiny fan crest** (the first dorsal fin): nine spines, scalloped membrane arcs, and bubbles on the front spines.
- **Doublet:** red half-hatch crossed by the **stitch line** (7 px dashes, 4 px gaps), with eight dusky **saddle** blocks in Aquifer across the shoulders and speckled sleeves.
- **Holds:** a halberd whose blade is a fanned tail fin, on a hatched shaft.
- **Glyph:** stitch dashes. **Divider:** ripple broken into stitches.

### ♣ THE GROVE

**K♣, The Cypress King** · `TAXODIUM DISTICHUM`
- **Who:** the bald cypress, patriarch of the banks, which can live 800–1,200 years (§2.7).
- **Gaze:** 3/4 left, with deep-set, patient eyes.
- **Beard:** two points of flat feathery sprays, combed off a rachis.
- **Crown:** seven **cypress knees** rising from ripple lines, fluted with half-hatch and outlined in gold.
- **Robe:** vertical fluting widening like a buttressed trunk, a mantle in red half-hatch (autumn russet), and a jade stole embroidered with sprays.
- **Holds:** the traditional orb as a gold **cypress cone** (a sphere of wrinkled scales), and a fluted-trunk scepter with a knee finial.
- **Glyph:** cone. **Divider:** doubled knee arcade.

**Q♣, The Pecan Queen** · `CARYA ILLINOINENSIS`
- **Who:** the pecan, state tree since 1919, which grows at Spring Lake (§2.8); she stands for harvest and plenty.
- **Gaze:** 3/4 right, with a warm half-smile.
- **Crown:** gold four-winged husks split open as quatrefoils, alternating with oval nuts, on a band of ridged-shell arcs.
- **Gown:** a bodice of half-hatched pinnate leaves meeting in chevrons, red panels, shell-ridged sleeves and a four-lobed husk collar.
- **Holds:** her flower as a pecan sprig with three nuts and pendant **catkins** (strings of small circles).
- **Glyph:** husk quatrefoil. **Divider:** beaded knee arcade.

**J♣, The Bobcat Knave** · `LYNX RUFUS`
- **Who:** the naturalistic bobcat, the stealthy hunter of the riverbank shade (§2.13). He is never a mascot.
- **Gaze:** 3/4 left, eyes cutting sideways to the right; watchful.
- **Hood:** close-fitting with black-tipped ear tufts, framing a facial ruff of short barred strokes.
- **Tunic:** *bobcat-spot ermine* over barred sleeves.
- **Holds:** a single fletched arrow upright (with a bubble nock) and a live-oak sprig with acorns.
- **Colour:** jade, Aquifer and paper only, with gold on the arrowhead alone. **No Gill Red**, so the cat never pairs with red and gold (§6).
- **Glyph:** spot cluster. **Divider:** plain knee arcade.

### ♥ THE HILL

**K♥, The Warbler King** · `SETOPHAGA CHRYSOPARIA`
- **Who:** the golden-cheeked warbler, the only bird that breeds only in Texas, recorded at Purgatory Creek (§2.19).
- **Gaze:** 3/4 right, head lifted mid-song.
- **Face:** the bird itself: a solid black **bib beard**, cheeks of **gold half-hatch** (the deck's only gold face), and a black stripe through the eye.
- **Crown:** his nest, a woven cup of Ashe-juniper bark strips, interlaced with gaps, the ragged ends standing as points.
- **Mantle:** black with two paper-white wing bars, lined in jade juniper scales.
- **Holds:** a juniper bough behind his head (the traditional K♥ blade) and an acorn orb.
- **Glyph:** juniper berry. **Divider:** doubled petal-engrail.

**Q♥, The Bluebonnet Queen** · `LUPINUS TEXENSIS`
- **Who:** the bluebonnet, state flower since 1901, with the paintbrush that blooms beside it (§2.10).
- **Gaze:** near-frontal, turned slightly left toward the J♥.
- **Crown:** five jade racemes of stacked keel-petals, the centre one tallest, each tip left paper-white.
- **Gown:** a bodice of palmate five-leaflet stars, sleeves hemmed with petal-engrail scallops, and a chevron stomacher.
- **Necklace:** five teardrops, the rain that falls on the Hill and sinks into the Deep.
- **Holds:** a bouquet of bluebonnets and paintbrush with **red-dipped bracts**, and a closed fan.
- **Glyph:** palmate leaf. **Divider:** beaded petal-engrail.

**J♥, The Monarch Herald** · `DANAUS PLEXIPPUS`
- **Who:** the monarch butterfly, state insect, funnelling through the Hill Country each October (§2.11); he announces the season.
- **Gaze:** one-eyed profile facing left, young, departing.
- **Cap:** a black herald's cap edged with double dot rows, with clubbed antennae as plumes.
- **Tabard:** a monarch wing: an Aquifer vein lattice with cells half-hatched in red and a dotted black margin.
- **Sleeves:** jade-striped.
- **Holds:** a gold trumpet with a swallowtail banner, and a split milkweed pod fanning silk.
- **Restraint:** a quiet nod, never the deck's hero.
- **Glyph:** two dots. **Divider:** plain petal-engrail.

---

## 8. Aces

**Shared layout for A♦, A♣ and A♥**
- An oversized pip, centred at y ≈ 470.
- The pip sits in a **plate mount**: a gold double circle 430 px across, with a 20 px band holding the suit's partition line bent into a ring.
- Below it, a plate label in Cinzel 600 at 4.5 pt, e.g. `— PLATE II · FLUMEN —`.
- The art is knocked out of the pip in paper; the mount is in gold.

**A♠, The Source · PLATE I · PROFUNDUM** (the showpiece, rule 16)

*The spade*
- A solid Aquifer spade 340 px wide (45 %), apex at y 150, with a buttress-flared stem ending at y ≈ 565.

*The emblem inside, in 0.5 pt gold*
- **Strata:** seven limestone bedding lines, stepped down 14 px across one diagonal fault (the Balcones break, and the ace's only asymmetry). Alternate beds are hatched.
- **Voids:** three karst voids break through the beds. In the central void (110 px) a **Texas blind salamander** curls in a single C along the wall. Its body is two parallel contours with ladder rungs (rule 11), with two dot eyes and three gill plumes per side.
- **Conduit:** from the void, two parallel lines rise up the axis to the upper third.
- **Rosette:** there the conduit opens into the **spring-vent rosette**: 16 half-hatched rays, three broken ripple rings and eight bubbles. A bubble string rises to the apex.

*Outside the spade*
- A **wild-rice laurel**: two sprays rise from below the stem and stop 20 px short of the shoulders.
- The leaves are half-hatched in Aquifer; the spikelets are gold.

*Legend* (gold, centred, y 640–800)
1. **ENDEMICS** in Playfair SC Black, cap 40 px, with inline.
2. `— PLAYING CARDS OF THE SAN MARCOS SPRINGS —` at 4.5 pt.
3. `FONS · NUMQUAM · DEFICIT` at 4 pt.
4. Set on a 900 px-radius arc: `SAN MARCOS · TEXAS · 72°`.

*Deliberately absent:* a crown in the spade, weapons, a skull, and a "TRADE — MARK" line split around the stem.

**A♦ · PLATE II · FLUMEN**
- Pip: a Gill Red diamond, 250 × 340.
- Knockout:
  - five wild-rice ribbon leaves streaming top to bottom in long S-curves with midribs;
  - one **fountain darter** crossing the widest point heading left (upstream), with its stitch line as knocked-out dashes.
- Mount: a ripple ring.

**A♣ · PLATE III · NEMUS**
- Pip: an Aquifer club, 280 px wide.
- Knockout:
  - each lobe holds a combed cypress spray radiating from the lobe centre;
  - the buttress stem carries three fluting lines.
- Below the stem, in gold outside the pip: three cypress knees rising from ripple lines.
- Mount: a knee-arcade ring, with the knees pointing outward.

**A♥ · PLATE IV · COLLIS**
- Pip: a Gill Red heart, 290 px wide.
- Knockout: a frontal, symmetric **monarch butterfly**.
  - The forewings fill the lobes and the hindwings meet at the point.
  - The veins are 0.75 pt paper lines.
  - A double row of paper dots follows the heart's edge 10 px inside.
- Mount: a petal-engrail ring.

---

## 9. Jokers

There are two jokers, deliberately different: one black and one red, for games that rank them.

**Shared layout**
- The figure occupies y 80–650.
- A 0.5 pt rule, 360 px long with bubble terminals, sits at y ≈ 690.
- The title (Cinzel 700, 7 pt, tracking +250) sits at y ≈ 740, and the subline (4.5 pt) at y ≈ 785.
- The stacked "JOKER" index is in the joker's colour.

**Black Joker: THE INTERLOPER** · `QUISCALUS MEXICANUS`
- **Who:** the great-tailed grackle. It is a Mexican species that barely reached Texas in 1900 and now runs the town (§2.12): the one non-native at a court of natives.
- **Pose:** upright in display, bill pointed skyward, with the **keel-shaped tail** folded like a hull.
- **Eye:** a gold ring with an Aquifer pupil (the yellow eye).
- **Stolen crown:** a small gold crown dangles from his bill, plainly stolen.
- **Plumage:** rows of scale arcs, with alternate feather tracts half-hatched in jade to suggest iridescence.
- **Perch:** a sagging downtown festoon wire with three bulbs (§4.4). No murals and no signage.
- **Call:** short dash-rays around the head.
- **Inks:** Aquifer, jade and gold.
- **Subline:** `— A NATIVE OF ELSEWHERE —`.

**Red Joker: THE SWINE DIVE**
- **Who:** the Aquarena show pig (§1.9). He is undated and unnamed, per §0.2.
- **Pose:** drawn with full dignity as a heraldic *pig volant*. He is small and rounded, streamlined mid-dive, with front trotters forward and ears swept back.
- **Porthole:** he plunges down through a riveted **porthole ring**, a double circle with 16 rivet dots taken from the Submarine Theater (§1.7).
  - His snout and trotters break out below the ring.
  - There is no sawtooth edge and no landscape vignette.
- **Bubbles:** a bubble trail curls behind him into a scroll.
- **Inks:** Gill Red, gold and Aquifer.
- **Subline:** `— LATE OF THE SUBMARINE THEATER —`.

---

## 10. Card back

**Flood**
- Spring Jade, 675 × 975 px, inset 37.5 px (0.125 in) from the trim.
- Flood corner radius 18 px (1.5 mm).
- All art is reversed out to paper, with knockout coverage **18–22 %** (rules 6–7).

**Symmetry.** The frame is mirror-symmetric on both axes (D2). The emblem is **180°-rotational only** (C2), so it keeps a sense of motion.

**Frame nesting**, from the flood edge inward:
1. **Outer rule:** 1.0 pt, inset 22 px.
2. **Ripple-and-bubble band:** 18 px wide. Two 0.5 pt rules enclose a sine ripple (wavelength 36 px, amplitude 4 px), with a 3 px bubble in each trough. It runs all the way round, with **no mottos**.
3. **Quarter-vent corners:** in each corner the band turns around a quarter-rosette (radius 52 px, seven half-hatched rays, three ripple arcs). A bubble string runs diagonally inward from each.
4. **Axis plinths:** at top and bottom centre, a small two-tread **fault-step plinth** (60 px wide) receives the lens tip.
5. **Mid-side stitch rules:** where the lens bellies approach the band, a 120 px rule: two 0.5 pt lines with a dashed line between them.
6. **Lens cartouche:** a tall **vesica** running from plinth to plinth, because Spring Lake is lens-shaped in plan (§1.1).
7. **Spandrels:** the four spaces between the lens and the band are filled with **six offset contours of the lens** at an 11 px pitch. Each contour dissolves into dashes toward the corners, like the lake's rings spreading outward.

**Central emblem** (inside the lens, C2)
- **The Source rosette** (230 px across):
  - a 14 px open core;
  - a ring of eight bubbles;
  - 16 rays alternating long and short, each split along its axis with one half hatched;
  - three concentric ripple rings broken at 22.5° steps;
  - an outer ring of 32 beads.
- **Two fountain darters** (95 px) orbit the rosette clockwise, each the 180° copy of the other. Each has a stitch line, eight saddle bars and a fanned dorsal fin.
- **Wild-rice pinwheel:** two ribbon leaves and two flowering stalks spiral clockwise out of the rosette toward the lens walls.
- **Lens tips:** a combed cypress spray ending in a round cone points into each tip.

**Restrictions**
- There is no text on the back.
- There is no vertical axis and no intertwined pair.

---

## 11. Tuck box

**Board.** Standard poker tuck: front 2.5625 × 3.5625 in (769 × 1069 px at 300 dpi), depth 0.75 in. Deep Hole `#102B2A` uncoated linen board, **one gold hot foil**, and blind emboss.

**Front.** The composition is bilateral. Its one dynamic element is the radiating rosette (rule 23); there is no diagonal band.
- **Border:** the back's frame, adapted (outer rule, ripple-and-bubble band, quarter-vent corners).
- **Top:** `— NATURAL HERALDRY —`, Cinzel 600 at 5 pt, tracking +250, on a 700 px arc.
- **Centre** (y ≈ 230–600):
  - a 300 × 380 px **lens** holding the gold vent rosette, **deeply embossed**, with 32 hairline rays escaping past the lens edge;
  - a wild-rice wreath of two sprays wrapping the lens and tied at the foot by a small swallowtail ribbon reading **NUSQUAM ALIBI**.
- **Specimen roundels:** four roundels, 70 px each, sit on the lens diagonals. Each holds a suit pip in outline, ringed by that suit's partition line. Clockwise they follow the water: ♠ fault-step (top-left) → ♦ ripple (top-right) → ♣ knee (bottom-right) → ♥ petal (bottom-left).
- **Wordmark** (y ≈ 700): **ENDEMICS**, cap 72 px, inline with hatched shadow, on a straight horizontal band with double rules and swallowtail ends. The band is embossed.
- **Subline:** `PLAYING CARDS OF THE SAN MARCOS SPRINGS`, Cinzel 700 at 6 pt, tracking +150.
- **Foot:** `SAN MARCOS · TEXAS` at 5 pt between two bubble-ended rules.

**Back.** The card-back art redrawn in gold foil line, with only the emblem embossed. The side margins are filled with vertical wild-rice ribbon lines, not stripes.

**Side 1.** Running vertically: `FONS NUMQUAM DEFICIT · THE SPRING NEVER FAILS`, with a combed cypress spray at each end.

**Side 2.** An acknowledgment in two lines at 5 pt: `THE SPRINGS HAVE BEEN CARED FOR BY INDIGENOUS PEOPLES FOR MORE THAN 12,000 YEARS`.
- Print it **only after review**, for example by the Indigenous Cultures Institute (§3.2, §6).
- Use no Indigenous-language words and no depiction.

**Top flap.** `SAN MARVELOUS` in tracked caps (§5.4), with a tiny vent rosette.

**Bottom flap.** The **ghost of the San Marcos gambusia**: an outline-only fish with no hatch. Beneath it, `GAMBUSIA GEORGEI · LAST SEEN 1983` at 4 pt (§2.5), as a quiet memorial.

**Seal**
- **Shape:** a 1.1 in round die-cut whose edge is **24 shallow ripple lobes**, like a spring ring. It sits across the flap.
- **Paper and print:** Limestone ivory paper, printed in Gill Red with gold foil.
- **Emblem:** one Texas blind salamander curled in a single C, with red gill plumes and dot eyes. There is never a pair.
- **Text:** `NUSQUAM ALIBI` arched along the top and `· ENDEMICS ·` along the bottom, with two bubble strings.

**Emboss** only the lens rosette, the wordmark band and the four roundels. The ground stays flat (rule 15).

---

## 12. Ornament vocabulary (unique to ENDEMICS)

| Ornament | Used on | How it is drawn |
|---|---|---|
| **Fault-step** (♠ partition) | ♠ dividers, back plinths, K♠ crown, ♠ roundel | A polyline of 16 px treads and 60° risers. Every third riser is doubled with a 5 px offset to show the fault's throw. |
| **Ripple** (♦ partition) | ♦ dividers, back band, A♦ mount | A sine curve, wavelength 36 px, amplitude 4–5 px. On Jacks it is broken into stitch dashes. |
| **Cypress-knee arcade** (♣ partition) | ♣ dividers, K♣ crown, A♣ mount | Knees 18 px wide at a 26 px pitch on a baseline. Each knee is a pointed arch of two arcs (r = 1.4 × width) capped by a 4 px circle. Alternate knees are fluted with vertical half-hatch. |
| **Petal-engrail** (♥ partition) | ♥ dividers, Q♥ hems, A♥ mount | Cusps of r = 10 px arcs spanning 16 px, points outward, with a 3 px dot on each point (the lupine's white tip). |
| **Spring-vent rosette** | Back, A♠, tuck, K♠ crown, J♠ lantern | Built from the centre out: core circle → eight bubbles → 16 rays, each split on its axis and half-hatched → three concentric rings broken by gaps → a bead ring. Circles only; not bank-note guilloche. |
| **Bubble string** | All free line ends, frame corners | Three circles of 3×, 2× and 1.4× the stroke, with gaps of 1.5× the stroke, along 45° or vertical. Replaces the circle terminal (rule 9). |
| **Wild-rice laurel** | A♠, tuck wreath, back pinwheel | A circular-arc stem with alternating leaf vesicas (length : width 9 : 1), half-hatched perpendicular to the midrib. The head has erect spikelets (3 : 1 vesicas with one awn line) above and drooping florets (teardrops on 12 px stalks) below. |
| **Darter stitch** | J♦, back mid-sides | A dashed line of 7 px dashes and 4 px gaps, with 2 px dots flanking every third gap. |
| **Strata coursing** | K♠ robe, A♠ | Horizontal beds 12–20 px high, with alternate beds hatched and one diagonal fault jog. Karst voids are rounded ellipses cut through the beds. |
| **Karst honeycomb** | K♠ robe | A hex grid of 14 px cells. Each cell is shrunk by `buffer(−2)` and then re-rounded with `buffer(+1.5)`. |
| **Combed cypress spray** | K♣, A♣, back, tuck side | A rachis arc with 18–26 single straight leaflets per side at 70°. Leaflet lengths taper by a sine curve. |
| **Bobcat-spot ermine** (the deck's heraldic fur) | J♣ | A quincunx grid at a 22 px pitch. Each spot is a solid Aquifer teardrop (6 × 9 px) with two 2.5 px dots above it. Rows are offset by half the pitch. |
| **Monarch vein lattice** | J♥, A♥ | Veins run as arcs from the wing root. Cells are half-hatched. The margin carries a double dot row. |
| **Husk quatrefoil** | Q♣ | Four vesicas around a 6 px circle, each ridged with three parallel arcs. |
| **Bluebonnet raceme** | Q♥ | A cone of stacked keel-petal pairs (two small arcs each), shrinking 8 % per tier. The top three tiers are left paper-white. |
| **Juniper weave** | K♥ crown | Two families of strips at ±30°, woven over-under with 1.5× stroke gaps at the crossings (rule 10). |
| **Gill plume** | Q♠, J♠, A♠, seal | A curved stem with 6–8 barbs per side, shortening toward the tip and ending in a bubble. Gill Red on paper. |
| **Lens offset field** | Back spandrels, tuck | Offset contours of the vesica (`shapely` buffer) at an 11 px pitch, dashed toward the corners. |
| **Plate mount** | Aces 2–4, tuck roundels | A gold double circle with the suit's partition line bent into a ring between the two circles. |

---

## 13. Build notes and open points

**Helpers** (shapely):
- `half_hatch(poly, axis, angle, pitch=7)`
- `partition(kind, x0, x1, y, amp)`, returning a LineString, with `band()` producing the line plus its 180° copy
- `vesica(a, b, r)`
- `rosette(...)`
- `bubble_string(p, dir)`
- `offset_field(shape, n, d)`
- `combed_spray(arc, n)`

Draw each court's upper half, then `rotate(180, origin=(375, 525))`. Convert all type to paths with fontTools.

**QA checks**
- Stroke widths must be in {2.1, 3.1, 4.2, 6.25} px.
- No hatch gap under 4.2 px.
- Back coverage 18–22 %, measured by raster count.
- Render with `rsvg-convert` at 750 px and at 190 px (hand-held size) to test index legibility.

**Open points**
- **Two bird kings (K♥ and K♦).** They are separated by pose (3/4 against profile), headwear (nest against crest) and colour (gold cheeks against a jade belt).
- **Details from general knowledge.** The J♥'s milkweed and the grackle's stolen crown come from general knowledge or invention, not the motif bible. Both are low risk.
- **Cinzel at 0.80 x-scale** must pass the 190 px legibility test. If it fails, fall back to cap 88 px at x-scale 0.85.
- **Ivory stock:** confirm the printer offers it, or fall back to white.
