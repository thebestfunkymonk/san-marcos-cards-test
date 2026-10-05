# Concept A: THE SPRING COURT

**Tagline:** *Long may it flow.*
**Wordmark line:** THE SPRING COURT · Royal Playing Cards · San Marcos, Texas
**Mottos (new Latin, two words each, for ribbons and seals):** *FONS REGNI* ("source of the kingdom") and *NUMQUAM DEFICIT* ("it never fails").

---

## 1. Narrative (≤150 words)

Where the Balcones fault divides Hill Country from plain, the Edwards Aquifer rises through more than two hundred spring openings that have never been known to stop. This is the throne of the Spring Court. Named for St. Mark in 1689, the kingdom took his winged lion as its arms: forepaws on limestone, hind paws in spring water. Four houses serve the Source:

- The **House of the Deep** (♠) keeps the aquifer's dark halls.
- The **House of the Fount** (♥) dances beneath the surface.
- The **House of the Reed** (♣) tends a wild-rice found nowhere else on Earth.
- The **House of the Ford** (♦) guards the old road's river crossing.

Every royal has a reflection: each court's lower head is the figure seen in the water. The spring never stops, so the crown never falls. Long may it flow.

*(Fact basis: 200+ openings, never known to stop, the Balcones fault line, the St. Mark name, and endemic Texas wild-rice all come from san-marcos.md §1.1, §1.4, §2.1, §3.3–3.4. Print only "Named for St. Mark · 1689", never a day.)*

---

## 2. Palette

The palette is a limestone ground, dark spring-water inks, and one gold. It stays restrained: three inks plus one metallic on the faces, one ink on the back, and one foil on the tuck.

| Token | Hex | Role |
|---|---|---|
| **Limestone** (paper) | `#F4EFE3` | Card ground. It is warm ivory, the colour of Edwards limestone and courthouse trim. Use a natural-white stock or a 4 % warm tint flood. It is also the reversed-out line colour on the card back. |
| **Aquifer** (ink 1) | `#14262B` | A near-black deep teal that reads as black at arm's length. Used for **♠ ♣ pips and indices**, all court and ace key lines, and the Trickster joker. |
| **Gill Carmine** (ink 2) | `#B22E2C` | Named for the blind salamander's red gills and the paintbrush bracts. Used for **♥ ♦ pips and indices**, court accents, and the Fool joker. |
| **Spring Jade** (ink 3) | `#1D5B56` | The "clear, dark turquoise" of Spring Lake. Used for court garment fills and the **card-back flood**. On the tuck it is the board colour. |
| **Lion Gold** (metallic / foil) | flat stand-in `#B39155`; foil preview gradient `#7E5F2A → #D6B46A → #F5E4A8` (preview renders only) | On the faces it is metallic ink (PMS 871/872 type) for crowns, regalia, ace emblems and ace legends; it may flat-fill small court garment panels. On the tuck it is the **only foil**, used for line and type only, never a flood (style rule 14). |

**Suit colours.**
- Red suits (♥ ♦) use Gill Carmine for pips, indices and the large court pip.
- Black suits (♠ ♣) use Aquifer.
- Courts use all four colours. As a secondary cue for the house, black-suit courts lean on jade and gold, and red-suit courts lean on carmine and gold.

**Card-back colourway.**
- Spring Jade `#1D5B56` flood with all art reversed out to Limestone paper.
- 0.125 in (37.5 px) unprinted border.
- Flood corner radius 18 px (≈1.5 mm).
- An optional later edition, "Carmine Court", uses a `#8C2A28` flood.

**Ink budget.**

| Piece | Inks |
|---|---|
| Faces | Aquifer + Carmine + Jade + metallic gold |
| Back | Jade only |
| Tuck | Jade stock + gold foil + blind emboss |
| Seal | Carmine paper + gold foil |

---

## 3. Typography

The whole deck uses one type superfamily, Cinzel, plus a single Cormorant accent word. That keeps it regal and restrained. Cinzel is also the right Roman-inscriptional voice for a heraldic court. All type is outlined to paths with `inkkit.typeset.text_to_path`. Sizes are for the 750 × 1050 px trim at 300 ppi, where 1 pt = 4.17 px.

### Indices

- **Face and size.**
  - **Cinzel wght 800**, rank cap height **90 px (0.30 in)**, font size 128.6 px.
  - Every rank is horizontally scaled **80 %**.
  - **"10" is scaled 70 % with −20 tracking**, which gives a width of ≈88 px.
- **Position.**
  - Index axis at **x = 80 px** from the left trim, with the rank and pip centred on it.
  - Rank cap top at y = 46 px.
  - The widest rank then spans x ≈ 36–124, so every glyph stays at least 36 px from the trim.
- **Two glyph fixes**, both verified in a mock render:
  - **J:** squash the descender (points with y > baseline get y × 0.45), so it drops only 12 px.
  - **Q:** rebuild it as Cinzel "O" plus a custom short wedge tail. The tail leaves the bowl at about 5 o'clock, falls 30° below horizontal, ends ≤12 px below the baseline and ≤8 px past the bowl. The stock Cinzel tail is 180 px wide and collides with the pip.
- **Index pip:** **72 px tall**, top 22 px below the rank baseline. The index block runs from y = 46 to y = 230.
- **Corners:** top-left and bottom-right only (bottom-right is rotated 180°). Sizes are identical on all 54 cards.
- **Joker index:** "JOKER" stacked vertically in the same face: cap height 44 px, 80 % scale, letter pitch 52 px, axis x = 66, with the J descender squashed.

### Wordmark (tuck, ace legend, seal)

- **"SPRING COURT"** in **Cinzel Decorative Black**. Its swashed R, G and S carry the fairy-tale note.
- Drawn as **inline + hatched shadow**:
  - an inner contour offset −3 px (at tuck scale), knocked out to stock;
  - a drop shadow offset 5 px down-right, filled with 45° parallel hatch (2.1 px lines at 6.9 px pitch) rather than solid.
- The small "the" above it is the one accent word, in **Cormorant Garamond 500 lowercase**.

### Small text (legends, captions, side panels)

- **Cinzel wght 600**, cap height 13–16 px (font size 19–23 px ≈ 4.5–5.5 pt).
- Tracking +200 to +250.
- Flanked by drawn em-rules: 2.1 px lines, 28 px long, with a 10 px gap.
- Numbers use Roman numerals where they are ornamental (MDCLXXXIX). Use Arabic figures where they must be read (12,000).

### Ace captions and joker captions

**Cinzel wght 700**, cap height 18 px, tracking +250.

**Avoid:** EB Garamond with the current `text_to_path`, which crashes on its composite digit glyphs. Also avoid Bodoni, whose hairlines vanish at index size, and the Playfair SC / IM Fell old-style figures in indices.

---

## 4. Line-weight system (750 × 1050 px)

The deck is monoline, per style.md §0 and rule 1. There are no swelling burin lines, no cross-hatching and no guilloche. "Engraved" richness comes from density, half-hatching and foil.

| Use | Weight |
|---|---|
| Base ornament line (back, tuck, ace emblems, patterns, hatching) | **2.1 px (0.5 pt)** |
| Frame and accent rules | **4.2 px (1.0 pt)** |
| Court contours | **6.25 px (1.5 pt)** |
| Court interior detail | **3.1 px (0.75 pt)** (2 : 1 contour-to-interior) |
| Hatch | 2.1 px lines at **6.9 px pitch** (4.8 px gap). Exactly one half of a split shape is hatched. |
| Circle terminals | Ø 6.3 px (3× stroke) on free line ends |
| Bead / bubble dots | Ø 4.2–8 px |
| Minimum stroke | 1.5 px |
| Knockouts inside solid pips | lines ≥ 2.5 px, gaps ≥ 3 px |
| Interlace | under-stroke broken with a 4 px gap on each side |

---

## 5. Suits and pips

| Suit | House | Theme | Pattern language |
|---|---|---|---|
| ♠ | **House of the Deep** | The Edwards Aquifer: limestone, karst, cave water, the Texas blind salamander, the Balcones fault | strata bands, fault-steps, karst-void ovals, drip fringe |
| ♥ | **House of the Fount** | Spring Lake's surface and the vents beneath it: mermaid heritage, bubbles, pearls, glass-bottom-boat wonder | scale lattice, ripple rings, bubble chains, pearl beading |
| ♣ | **House of the Reed** | The riverbanks: Texas wild-rice, bald cypress, kingfisher, heron, pecan | ribbon leaves (half-hatched), comb sprays, cypress-knee crenellation, pecan pinnate repeats |
| ♦ | **House of the Ford** | The Camino Real crossing and the town: courthouse dome, Justice, compass, spur rowels, tooled leather | ashlar courses, arcades, rowel stars, stepping-stone chains, tooled scroll |

### Pip silhouettes

Pips are standard, and the bespoke touches are at silhouette level only. Every pip is a **solid fill in its suit ink with no internal ornament**. This applies to 2–10, the indices and the large court pips, and it keeps playability first (Monarchs' restraint). The only changes are to the outline:

- **Spade:** classic Bicycle proportions, with lobes about 4 % fuller. The flared stem ends in a **fault-step foot**: two stacked trapezoids, the lower one 1.35× wider, joined by a 3 px step. This is the Balcones step.
- **Club:** three near-circular lobes ("three bubbles") with a slight overlap, and the same fault-step foot. This ties the two black suits together.
- **Heart:** the standard heart, but the top cleft closes on a **round notch** (radius 4 % of pip width) instead of a sharp V, like a bubble resting in the fluke.
- **Diamond:** sides very slightly **concave** (sagitta 3.5 % of side length), like a cut ford-stone. The tips stay sharp.

### Sizes and layout

- **Number-card pips:** 116 px tall, in the standard USPCC layout. Columns sit at x = 222 / 375 / 528, and the top and bottom rows are centred at y = 190 and 860. The lower-half pips are rotated 180°.
- **Index pip:** 72 px.
- **Court frame pip:** 100 px.
- Pip silhouettes are built once as `<symbol>`s and reused everywhere, which keeps their identity exact across all 54 cards.

---

## 6. Court system (shared by all 12)

**Composition**
- Classic **two-headed half-figures**. The top half is drawn once and rotated 180° about the card centre (`inkkit.card.two_headed`).
- Story: the lower head is the figure's **reflection in the spring**. The divider is always a water or earth line that passes through the card centre and is C2-symmetric.

**Frame**
- A single **4.2 px Aquifer rule**. The box runs from (138, 50) to (612, 1000), so it is centred and clears both indices by ≥14 px.
- **Chamfered "ashlar" corners:** 14 px cuts at 45°. Each chamfer holds that house's small mark:

  | House | Chamfer mark |
  |---|---|
  | ♠ | a 10 px fault-step notch |
  | ♥ | a Ø 8 px bubble |
  | ♣ | a reed-node ellipse |
  | ♦ | a 10 px lozenge |

- The large 100 px court pip sits inside the frame, 18 px from the sides, in the upper corner named in each brief. A rotated copy sits in the opposite lower corner.

**Dividers.** The rank sets the direction and the house sets the line.

| Rank | Direction |
|---|---|
| Kings | horizontal |
| Queens | rising diagonal (bottom-left → top-right) |
| Jacks | falling diagonal (top-left → bottom-right) |

| House | Line |
|---|---|
| ♠ **Fault-step** | double rule (4.2 px + 2.1 px, 6 px apart) with one 18 px Z-step at the centre |
| ♥ **Ripple** | two parallel sine waves 8 px apart, 2.5 periods across the box, with a zero-crossing at the centre |
| ♣ **Reed** | a single 4.2 px stalk with a node ellipse (20 × 10 px) at the centre, plus paired 12 px leaf-ticks every 60 px, arranged C2 |
| ♦ **Ford** | a double rule 10 px apart with 10 px lozenge "stepping stones" every 40 px between the rules, and an 18 px central lozenge |

**Face kit.** Invented faces only: no likenesses, and no real Aquamaids or musicians.
- Almond eyes are two arcs with a heavy upper lid at contour weight, and a solid pupil dot.
- The nose is one straight ridge line with a small hook.
- The mouth is a short bow plus a lower-lip tick. Brows are single arcs. The ear is a C.
- The face has at most 14 strokes and is left paper-white.
- **Hair and beards are "current lines":** locks of 3–5 parallel offset curves at 7 px pitch, ending in circle terminals, as if the hair were drawn by flowing water.
- Hands are simplified mitts with three finger lines.

**Fills.** Flat Jade, Carmine or gold panels, with patterns drawn over them in Aquifer or knocked out to paper. There are no gradients. Every court wears the **Lion Mark** somewhere: as a clasp, badge, finial or banner. It is the kingdom's hallmark.

---

## 7. Court briefs

### K♠: The King Beneath (Keeper of the Aquifer)
- **Who:** The eldest sovereign, lord of the aquifer's drowned halls. He is the deck's only strictly frontal figure.
- **Wears:** A mantle in **strata bands**, with alternate courses hatched at 45°. The tunic is dotted with karst voids, the hem has a fault-step border, and a gold Lion Mark clasp sits at his throat.
- **Holds:** A Lion Mark sceptre (viewer's right) and a **spring-vent orb**: ripple latitudes with a bubble where the cross would be.
- **Crown:** The **Escarpment Crown**: merlons rising in three fault-steps to a centre peak.
- **Face:** Forked current-line beard; level, heavy-lidded gaze.
- **Divider:** Horizontal fault-step.
- **Colour:** Jade mantle, carmine lining and one crown gem, gold regalia.
- **Pip:** Top-left.

### Q♠: The Blind Oracle (Queen of the Hollow)
- **Who:** The seer of the cave waters. Like the blind salamander, and like a player's blind bet, she sees without eyes.
- **Wears:** A paper-white gown with contour hatching. Her ruff is **six feathery gill-plumes** in carmine, the only bright red on a spade court. Drip-fringe cuffs.
- **Holds:** A **scrying mirror of still water**. A blind salamander appears inside its ripple rings as a vision (eye-dots, spindly legs, finned tail). It is never held in her hand.
- **Crown:** A **stalactite diadem**: graduated drips veiling her brow.
- **Face:** Eyes closed, 3/4 left, serene.
- **Divider:** Rising-diagonal fault-step.
- **Colour:** Jade mantle, carmine gills, gold diadem.
- **Pip:** Top-right.

### J♠: The Lantern Page (Page of the Deep)
- **Who:** The young keeper who carries light down the aquifer's conduits.
- **Wears:** A short-caped hood, a **fault-line doublet** of stepped chevrons, a belt of karst-void rings, and a rope coil drawn as a helix of diagonal ticks.
- **Holds:** A **hexagonal lantern** on a short chain, with ray-lined panes and a vesica flame. Its cap is cast as a coiled dark San Marcos salamander, a sculpted answer to the Queen's pale one.
- **Headwear:** A stepped hood crest with a Lion Mark badge.
- **Face:** Near-profile 3/4 right, looking up at the light (the one-eyed jack nod).
- **Divider:** Falling-diagonal fault-step.
- **Colour:** Jade doublet, carmine hood, gold lantern.
- **Pip:** Top-left.

### K♥: The Ferryman King (King of the Fount)
- **Who:** Sovereign of Spring Lake's surface and showman of glass-bottomed wonders.
- **Wears:** A robe of **ripple rings** with pearl-beaded trim. His breastplate is a **gold-framed glass-bottom window** showing ripples, two ribbon plants and one fountain darter with its stitch-dash flank.
- **Holds:** A **punting pole** diagonal behind his head, a nod to the traditional sword behind the heart king's head, and a vent-engraved chalice trailing bubbles.
- **Crown:** Seven graduated **bubble finials** on slender stalks.
- **Face:** Curled current-line beard; 3/4 left, kindly, eyes on the chalice.
- **Divider:** Horizontal ripple.
- **Colour:** Carmine robe, jade window, gold crown and chalice.
- **Pip:** Top-right.

### Q♥: The Aquamaid Queen (Queen of the Fount)
- **Who:** Queen of the maids who dance beneath the springs. She is the city's mermaid heritage made regal, with an invented face.
- **Wears:** A **scale-lattice** bodice running down to the divider, so her tail stays hidden below the waterline. Her sleeves carry wave-lines. A pearl collar, and a **ribbon of rising bubbles** from her shoulder (the Aquamaid air hose, reimagined).
- **Holds:** An **arrowhead** stem: an arrow leaf and a three-petalled flower from the vents.
- **Crown:** A **fan tiara of graduated pearls**.
- **Hair:** Gold current-lines threaded with bubbles.
- **Face:** 3/4 right, half-lidded, faint smile.
- **Divider:** Rising-diagonal ripple.
- **Colour:** Carmine bodice, jade sleeves, gold hair and tiara.
- **Pip:** Top-left.

### J♥: The Spring Minstrel (Page of the Fount)
- **Who:** The court troubadour who sings at the water's edge. He nods to the town's songwriting tradition but depicts no real musician.
- **Wears:** A tunic with **bubble-chain piping**, sleeves slashed with ripple arcs, and a running-wave sash.
- **Holds:** A **fiddle** upright at his shoulder (volute scroll, f-holes, four strings). The bow crosses his body, with interlace gaps behind his hand.
- **Headwear:** A beret with one long curling plume, pinned with a fluke-heart brooch.
- **Face:** Near-profile 3/4 left, eyes lowered to the strings (the one-eyed jack).
- **Divider:** Falling-diagonal ripple.
- **Colour:** Carmine tunic, jade beret, gold fiddle.
- **Pip:** Top-right.

### K♣: The Cypress King (King of the Reed)
- **Who:** The elder of the banks, as long-lived as a bald cypress (800–1,200 years).
- **Wears:** A robe of **fluted bark**: vertical contour lines like buttress flutes. A **comb-spray cypress** collar and a hem of cypress-knee crenellation.
- **Holds:** A cypress staff with a **belted kingfisher** perched on top (ragged crest, dagger bill: the king-fisher pun). His orb is a round **cypress cone** of scale-plates.
- **Crown:** The **Knee Crown**: five rounded cypress knees of varied height.
- **Face:** Root-twisted current-line beard; 3/4 left, heavy-lidded, sage.
- **Divider:** Horizontal reed.
- **Colour:** Jade robe, gold foliage and crown, carmine kingfisher breast band.
- **Pip:** Top-right.

### Q♣: The Wild-Rice Queen (Queen of the Reed)
- **Who:** Gardener-queen of the rarest grain, Texas wild-rice, which grows only in the upper San Marcos River.
- **Wears:** A gown of **ribbon leaves streaming diagonally with the current**, each a half-hatched vesica. Reed-ladder lacing and an egret-plume brooch.
- **Holds:** A gold **sceptre wrought as a flowering wild-rice stalk**: erect female spikelets above and drooping male florets below, botanically correct. It is regalia, not cut plants.
- **Crown:** A **rice-spike coronet** of upright spikelets on fine pedicels.
- **Face:** 3/4 right, calm, eyes on the sceptre.
- **Divider:** Rising-diagonal reed.
- **Colour:** Jade gown, gold sceptre and coronet, carmine lining.
- **Pip:** Top-left.

### J♣: The River Squire (Page of the Reed)
- **Who:** The squire who runs the river from springs to sea, in the spirit of the 260-mile Water Safari. The race is not named on the card.
- **Wears:** A **pecan pinnate-leaf** jerkin, a buckle shaped as a four-winged pecan husk splitting open, and comb-spray cypress sleeves.
- **Holds:** One long **canoe paddle held upright like a halberd**, blade up and half-hatched at 45°. It is shown at rest: never crossed, never in a shield.
- **Headwear:** A brimmed cap with a great-blue-heron plume streaming back in an S.
- **Face:** 3/4 left, alert, looking downstream.
- **Divider:** Falling-diagonal reed.
- **Colour:** Carmine jerkin, jade sleeves, gold paddle band and buckle.
- **Pip:** Top-right.

### K♦: The Warden of the Ford (King of the Ford)
- **Who:** Guardian of the crossing where El Camino Real meets the river, and law-giver of the square.
- **Wears:** A tabard of **ashlar courses** (rusticated limestone in running bond, from the courthouse base). A sash of **rowel stars** and tooled-scroll cuffs.
- **Holds:** The **Key of the Ford**, with a rowel-star bow and fault-step bit. It is a single key only.
- **Crown:** The **Dome Crown**: a ribbed dome on an arched drum with a lantern finial, drawn from the courthouse dome.
- **Face:** Squared beard; near-profile 3/4 right with one eye showing (the one-eyed king).
- **Divider:** Horizontal ford.
- **Colour:** Carmine tabard, jade sash, gold crown and key.
- **Pip:** Top-left.

### Q♦: The Queen of Scales (Queen of the Ford)
- **Who:** Justice of the square, after the figure on the courthouse dome. She weighs the kingdom's water.
- **Wears:** A gown in an **arcade** of keystoned round arches (the courthouse windows). A stomacher of four fluted column shafts and a cape edged with a stepping-stone chain.
- **Holds:** **Balance scales** held aloft, each pan holding ripple rings, and a sprig of **Texas paintbrush** with carmine bracts.
- **Crown:** A **portico diadem**: a pediment with an oculus over four column-teeth.
- **Face:** 3/4 right, eyes open and level. This Justice sees, as a counterpoint to the Blind Oracle.
- **Divider:** Rising-diagonal ford.
- **Colour:** Jade gown, gold scales and diadem, carmine paintbrush.
- **Pip:** Top-right.

### J♦: The Herald of the Road (Page of the Ford)
- **Who:** The court's messenger on the Camino Real, announcing arrivals at the crossing.
- **Wears:** A tabard of **rowel stars in a half-drop grid**, a map-scroll in his belt (a route line with river-crossing ticks), and tooled-scroll cuffs.
- **Holds:** A long straight **herald's trumpet** hung with a square banner bearing the **Lion Mark**, fringed with drip terminals.
- **Headwear:** A flat cap trailing two long, forked **scissor-tailed flycatcher** feathers.
- **Face:** 3/4 right, lips closed, gaze along the trumpet.
- **Divider:** Falling-diagonal ford.
- **Colour:** Carmine tabard with gold rowels, jade banner, paper cap.
- **Pip:** Top-left.

---

## 8. Aces

All three non-spade aces share one system:
- a solid suit pip 300 px tall (40 % of card width);
- a **2.1 px gold keyline** offset 8 px outside it;
- one ornament **knocked out to paper** inside it;
- one gold device outside it;
- a Cinzel 700 caption in gold at y ≈ 800, flanked by em-rules.

### A♠: The Lion of the Source (showpiece)
- **Spade:** A large **solid Aquifer spade 340 px wide (45 %)**, centred at y ≈ 440, with the fault-step foot.
- **Emblem inside the spade**, all in gold 2.1 px monoline:
  - **Lion:** the **winged lion in moleca**. It is frontal. The head sits in the upper centre, with a mane of three rings of scalloped arcs. The two wings rise from behind the mane and **curl inward to fill the spade's lobes**: three rows of scalloped coverts, then five long vesica primaries with one half of each hatched.
  - **Paws and vent:** The forepaws rest on the rim of a **spring vent** at the spade's waist: elliptical ripple rings with 12 radial ribs.
  - **Stem:** The stem is **stratified Edwards limestone**, five courses with alternate courses hatched at 45°.
  - **No crown and no halo or book.** The wings are his crown, which keeps it secular and well clear of Monarchs' crown-in-spade.
- **Outside the spade, in gold:**
  - A broken **waterline** at the spade's waist: three ripple dashes each side.
  - Two mirrored **columns of bubbles** at x = 375 ± 230, and **the bubbles grow as they rise**.
- **Legend** below the spade, centred and in gold:
  1. **THE SPRING COURT** (Cinzel 700, cap 20 px)
  2. **— ROYAL PLAYING CARDS —** (Cinzel 600, cap 13 px)
  3. **SAN MARCOS · TEXAS**
  4. **NAMED FOR ST. MARK · MDCLXXXIX**, set on an **arched baseline**.

### A♥: The Fount
- **Pip:** A carmine heart. It is read as the mermaid's tail fluke.
- **Knocked out to paper:**
  - The lobes are filled with **scale lattice**.
  - A **vent crater** sits low on the centreline (a circle with 8 curved ribs).
  - A column of **five graduated bubbles** rises from it to the cleft's round notch.
- **Outside:** A **gold pearl swag**, a catenary of 15 graduated pearls with a single drop pearl, hung beneath the point.
- **Caption:** HOUSE OF THE FOUNT.

### A♣: The Reed
- **Pip:** An Aquifer club.
- **Knocked out to paper:** A **wild-rice spray**. The centre stalk rises from the stem into the top lobe and ends in erect female spikelets. Drooping male florets fall into the side lobes. Two half-hatched ribbon leaves sweep from the stem base.
- **Outside:** A gold **wild-rice laurel**, a half-wreath of vesica leaves cupping the club's base from 4 o'clock to 8 o'clock, tied with a small reed-node knot.
- **Caption:** HOUSE OF THE REED.

### A♦: The Ford
- **Pip:** A carmine concave diamond.
- **Knocked out to paper:**
  - An **eight-point compass rose**. The N/S/E/W points align with the diamond's tips, and the diagonals are shorter.
  - Each point is a split lozenge with one half hatched.
  - A small vent circle sits at the hub.
- **Outside, in gold:** **The Crossing**.
  - A horizontal **triple wave-line river** passes behind the diamond (±210 px).
  - A vertical **dotted road line** crosses it (±250 px).
  - The diamond sits exactly at the ford, a single clear reading of the Camino Real at the river.
- **Caption:** HOUSE OF THE FORD.

---

## 9. Jokers

The two jokers are deliberately different, which settles big versus little joker at a glance. Both follow style rule 17: one figure, a thin horizontal rule, a tracked caption, and a vertical "JOKER" index. The Ralph name, dates and Aquarena branding are not printed.

### Big Joker: The Court Fool (Carmine + gold + Aquifer)
- **Figure:** A heraldic **pig volant in a swine dive**, drawn with complete dignity.
  - The body is a streamlined arc-built ellipse, with trotters forward, ears swept back and a curled tail.
  - He wears a tiny five-point jester collar with bell circles.
  - He plunges head-first toward a **splash crown**: seven water-drop points (vesicas with circle terminals) rising from ripple rings. It is the only crown the Fool ever wins.
  - A **helical bubble trail** rises behind him and resolves into a running-wave scroll near the top.
- **Caption:** THE COURT FOOL / — FORTUNE FAVORS THE FOOLHARDY —
- **Index:** Carmine.

### Little Joker: The Court Trickster (Aquifer + gold)
- **Figure:** A **great-tailed grackle in display**.
  - The bill points to the sky, and the tail is folded into a **keel** (a tall V).
  - The **yellow eye is a single gold dot**.
  - A **stolen coronet** is hooked on the tip of its bill.
  - It stands on one cypress knee.
  - Half-hatched feather groups suggest the gloss, and the second hatch half is gold on the wing coverts.
- **Caption:** THE COURT TRICKSTER / — LOUDEST IN THE KINGDOM —
- **Index:** Aquifer.

---

## 10. Card back: The Source

**Geometry**
- Spring Jade flood inset 37.5 px, with an 18 px flood radius. All art is reversed out to paper.
- Lines are 2.1 px, and frame rules are 4.2 px.
- Target knockout coverage is **18–22 %** of the flood. Measure it with `geom.area`.
- **No text on the back.**

**Symmetry.** The frame is **D2** (mirrored on both axes). The central emblem is **C2 only**: identical under 180° rotation, but deliberately not a mirror. The swirl of the rosette and the direction of the current give it motion.

**Frame, from the flood edge inward**
1. **Outer rule** of 4.2 px, inset 10 px, with a 2.1 px companion rule 8 px inside it.
2. **Vent-roundel corners**, which replace stepped Deco corners. At each corner the double rule is interrupted by a Ø 52 px roundel: an outer circle, an inner circle of Ø 16 px, and 12 **straight** radial ribs. The ribs are straight so the corners stay achiral for D2.
3. **Top and bottom bands** (34 px tall) carry a **running-wave scroll** (Vitruvian wave, 30 px pitch, 10 px amplitude) between two rules. The waves **flow outward from the centre** and are mirrored at the vertical axis, where they meet a small **Lion Mark** (Ø 60 px). The mark is upright at the top and rotated at the bottom.
4. **Side bands** (22 px wide) are **reed ladders**: two rules 16 px apart with rungs every 26 px and a node ellipse on every fourth rung. There is no motto on the long edges.
5. **Long-side midpoints:** a **wild-rice spikelet spray** of three erect spikelets on pedicels points inward and breaks the inner rule. It replaces the sunburst fans.
6. **Inner cartouche:** the **double-arch "fountain niche"**. The sides are straight, and the top and bottom edges are **segmental arches** that bow outward 36 px at the centre. It is a single rule plus a parallel rule 6 px inside, with a Ø 6.3 px circle "rivet" at each of the four corners.

**Central emblem** (overall width ≈ 440 px, about 75 % of the cartouche)
- **Source Rosette**, Ø 300 px, at the card centre. From the centre outward:
  - a vent crater (r 22 px) with 8 curved ribs;
  - ripple rings at r 34 / 44 / 56;
  - a **bubble-beading** ring at r 70 (24 circles of Ø 8 px);
  - a **pinwheel band** from r 82 to 118: 24 ribs, each a circular arc twisted 25° clockwise, with alternate cells half-hatched;
  - a **running-wave ring** (r 126–142) flowing clockwise;
  - an outer rule at r 150.
- **Lions:** the **Lion Mark in moleca** (≈150 px wide) rises from the top rim, forepaws on the rosette. A second one, rotated 180°, sits on the bottom rim, the kingdom and its reflection. The lions sit on the axis but never intertwine.
- **Wild-rice current:** five long **ribbon leaves** spring from behind the rosette at 9 o'clock. They sweep down and to the left and are half-hatched perpendicular to the midrib. One flowering stalk carries spikelets. The 3 o'clock spray is the same spray rotated 180°, so it sweeps up and to the right. This gives C2 motion.
- **Bubble triads:** four sets of three graduated bubbles fill the diagonal quadrant gaps, placed C2. Keep at least one leaf-width of flat jade between motifs.

---

## 11. Tuck box

**Stock and finish**
- **Spring Jade stock**, uncoated or soft-touch.
- **Gold foil only**.
- **Blind emboss** on the wordmark, the lion and the niche rim.
- Poker tuck front ≈ 2.5625 × 3.5625 in, depth 0.75 in. Use the printer's dieline.

**Front.** The layout is bilateral, with **one dynamic element**: the lion.
- **Frame:** the card-back frame vocabulary: outer double rule, vent-roundel corners, reed-ladder side bands, and running-wave bands top and bottom.
- **Wordmark:**
  - Upper third: a small lowercase "the" in Cormorant.
  - Then **SPRING COURT**, arched like a **gateway lintel** on a gentle arc (radius ≈ 2.2× the text width). It uses the inline + hatched-shadow treatment.
- **Centre:** the double-arch **fountain niche**. It holds the **winged lion *andante*** in profile, walking left: **forepaws on a stratified limestone ledge** (three courses, half-hatched) and **hind paws in spring water** (three ripple lines). This is the literal Balcones image.
  - The wings are upswept rows of scalloped feathers.
  - The tail curls up into a tuft.
  - Nothing else in the layout breaks the symmetry.
- **Below the niche:**
  - A level swallowtail **ribbon reading FONS REGNI**.
  - Then ROYAL PLAYING CARDS (Cinzel 700, tracked), an em-rule, and SAN MARCOS · TEXAS.
- **Not used:** diagonal bands, coin seals, lattice panels, shields.

**Back.** The full card-back design in gold foil, with the central rosette embossed. The side margins are filled with vertical reed-ladder.

**Sides**
- **Long side A:** THE SPRING COURT, set vertically between running-wave bands, then **LONG MAY IT FLOW**.
- **Long side B:** **"SEVENTY-TWO DEGREES · EVERY DAY OF THE YEAR"**, then the acknowledgment line **"The springs have been cared for by Indigenous peoples for more than 12,000 years."** It is set in Cinzel 600 at 4.5 pt. **Have the Indigenous Cultures Institute review this wording before print.** It is words only: no imagery and no Indigenous-language text.

**Flaps**
- **Top flap:** **SAN MARVELOUS** in tracked caps, with a tiny diving pig (the Fool) as an Easter egg.
- **Bottom flap:** a single **outline-only ghost fish** (the San Marcos gambusia, drawn with no hatching) above the words **GAMBUSIA GEORGEI · LAST SEEN 1983**, a quiet memorial.

**Seal**
- A **round die-cut seal with a 24-lobe ripple-scalloped edge**, Ø ≈ 1.1 in, folded over the top edge.
- Gill Carmine paper with gold foil.
- It carries a centred **Lion Mark**, **NUMQUAM DEFICIT** arched above, and **MDCLXXXIX** arched below, inside a **wild-rice laurel** ring.

---

## 12. Ornament vocabulary (unique to this deck)

All ornaments are built from circles, arcs and straight lines, per style rule 4. Construction assumes `inkkit` (shapely/skia geometry, `hatch.*`, `stroke.variable_stroke`, `card.rot180/mirror`).

1. **Source Rosette.** Build concentric rings from the centre outward: crater circle → ripple rings (radii in a 1.28 geometric step) → bubble-beading ring → **pinwheel band** (N ribs, each a circular arc from r₁ to r₂ rotated by a constant twist θ; alternate cells half-hatched with `hatch.parallel`, clipped) → running-wave ring → outer rule. It is C_N rotational, so it is C2-safe. For D2 use, drop the twist (straight `hatch.radial` ribs).
2. **Lion Mark (in moleca).** Build it once as a `<symbol>` and scale it from 36 px (clasp) to 340 px (ace).
   - Face: a circle with almond eyes, a trapezoid nose and a closed mouth.
   - Mane: 2–3 rings of scalloped arcs (12 outer scallops).
   - Wings: two sickle arcs that curl over the head. Each wing has three rows of scalloped coverts and five vesica primaries, one half of each hatched.
   - Two paws rest on a ripple line.
   - There is no halo and no book.
3. **Wild-rice ribbon leaf.**
   - Midrib: an S made of two tangent circular arcs.
   - Outline: `stroke.variable_stroke` along the midrib with a vesica width profile (length:width 10–14 : 1), then outlined at 2.1 px.
   - Split the polygon along the midrib and hatch **one** side perpendicular to the midrib, at 6.9 px pitch.
4. **Wild-rice spikelet spray.** A straight or arc stalk. **Erect female spikelets** above are 3:1 vesicas on 6 px pedicels at ±15°. **Drooping male florets** below are the same vesicas hung at ±150°. The spray is used in crowns, sceptres, frame midpoints and the A♣.
5. **Wild-rice laurel.** A wreath arc (or half-arc) with paired ribbon-leaf vesicas every 14°. Leaves shrink 6 % per pair toward the tips, and the ends are tied with a reed-node knot. It replaces classical laurel and olive.
6. **Running-wave scroll** (Vitruvian wave). A repeated unit of a circular-arc curl (a quarter-circle rising into a semicircle curl) at a fixed pitch between two rules. It is directional, so on D2 frames it is mirrored at the centre and flows outward. On rings it flows clockwise.
7. **Ripple rings.** Groups of three concentric circles or arcs with gaps growing 1.3× outward (`hatch.concentric`). Used on garment repeats, mirrors, pans and waterlines. This deck has no bank-note guilloche.
8. **Bubble beading.** Rows of circles whose diameters grow geometrically (×1.2) **in the direction of rise**. Ø 4–8 px on backs and up to 14 px on the ace. It replaces dotted-square beading.
9. **Fault-step.** A line broken by one right-angle step whose height is 4× the stroke (8–18 px). Used for the ♠ divider, the chamfer marks, the Escarpment Crown and the pip feet. It is the Balcones escarpment drawn as a single geometric gesture.
10. **Strata bands.** Horizontal courses of alternating heights (ratio 1 : 1.6), with every other course hatched at 45°. Used on the K♠ mantle, the A♠ stem and the tuck lion's ledge.
11. **Karst voids.** A staggered grid of ellipses in three sizes (Ø 6 / 10 / 16 px), drawn in outline, with a 2.1 px inner offset on the largest. Used on ♠ garments and belts.
12. **Drip fringe.** Vertical strokes whose lengths follow a slow sine envelope, each ending in a Ø 6.3 px circle terminal. Used on the stalactite diadem, cuffs and banner fringes.
13. **Scale lattice.** Rows of semicircular arcs, each row offset by half the pitch and stepped down by 0.6 × the radius. Clip it to the shape. Used on the ♥ bodice, the A♥ lobes and the K♥ trim.
14. **Cypress-knee crenellation.** Rounded conical knobs, each built from two arcs meeting in a small top fillet, in varied heights (1.0 / 0.8 / 0.65). Used on the K♣ crown and hems, and as the joker's perch.
15. **Comb spray** (cypress foliage). A straight or arc rachis with evenly spaced short parallel ticks on both sides. Tick lengths follow a vesica envelope, so the sprays read as flat, feathery cypress leaves.
16. **Reed ladder.** Two parallel rules with rungs at node intervals and a small node ellipse every fourth rung. Used on back and tuck side bands, bodice lacing and the tuck's back margins.
17. **Ashlar courses.** Running-bond rectangles with 3 px chamfered corners, drawn as rusticated limestone. Used on the K♦ tabard and the Dome Crown drum.
18. **Arcade.** A row of round arches, each a semicircle on two short jambs with a small keystone wedge. Used on the Q♦ gown and the Dome Crown openings.
19. **Rowel star.** An eight-point star wheel with a circle hub. The points are split lozenges with one half hatched. Used on the ♦ sashes and tabards, the key bow and the A♦ compass logic.
20. **Stepping-stone chain.** Lozenges spaced evenly between a double rule, with a larger central stone. Used for the ♦ divider and cape edges.
21. **Tooled scroll.** A vaquero floral-tooling scroll: a volute of tangent circular arcs with one vesica leaf at each turn. It replaces acanthus. Use it sparingly on ♦ cuffs and belts only.
22. **Current lines.** Hair, beards, plumes and river ribbons: 3–5 parallel offset curves at 7 px pitch (`geom.offset` of one guide), each ending in a circle terminal.
23. **Pearl swag.** A catenary of graduated circles, largest at the lowest point, with an optional single drop pearl.
24. **Double-arch fountain niche.** A rectangle whose top and bottom edges are outward-bowing segmental arches, drawn as a double rule with circle "rivets" at the corners. It is the deck's cartouche, used on the back, the tuck front and the court frame corners.

---

## 13. Guardrails (checked against style.md §10 and san-marcos.md §6–7)

**Kept clear of Jinkins**
- There is no sword or axis with intertwined creatures. The lions sit apart, above and below a rosette.
- There are no stepped Deco corners with dotted beading, and no Latin edge-motto on the long sides.
- There is no crown inside the ace spade.
- There is no penny-farthing, sawtooth-medallion joker, diagonal tuck banner, arrow or paddle shield, coin seals, lattice panels, serpentine road spine, or landscape roundel. There is no "ESTO…" crown seal. The mottos are new.

**Sensitivities**
- **The lion is secular:** no halo, no book, no *PAX TIBI* inscription, and it never appears on a joker.
- **Indigenous heritage:** no Indigenous imagery. The acknowledgment is text only, and ICI must review it.
- **University:** no bobcat, no Texas State marks, and no maroon-and-gold.
- **Real people and marks:** no real people, no Aquamaid likenesses, and no mermaid-statue references. There are no civic, Aquarena or venue marks.
- **Endangered species** are drawn accurately and never held by a figure:
  - salamanders appear as a vision or as sculpted ornament;
  - wild-rice appears as gold-wrought regalia.

**Feasibility**
- Every piece is frontal, mirror-symmetric or C2.
- Courts are built from a shared face kit, dividers and frame.
- The most complex drawings are the andante lion on the tuck and the Fool. Both are single heraldic profiles built from arcs. If the andante lion over-runs, the fallback is the Lion Mark in moleca.
