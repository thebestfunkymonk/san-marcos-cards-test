# HEADWATERS court guide

How to draw a court so that all twelve look drawn by one hand. The brief
(`research/creative-brief.md`) is law; this guide is the method. The hand is
`deck/courtkit.py`; the worked example is `art/KS.py` (K♠ · The King Beneath).
Read `deck/ART_CONTRACT.md` first for how a module plugs into the deck.

### Continuous courts

The recipe below describes the existing band-mode courts. For a continuous
double-head, compose the full C2 scene with `K.Scene(rank=None)`, do not add
`K.band_guard`, and set `DOUBLE_HEAD = "continuous"` plus a `SEAM` accepted by
`deck.frames`. `rank=None` means no band clip or band-rule healing; the build
system clips and rotates the finished art. Build every seam-crossing garment
as C2 art with `K.c2(...)`, or extend it past the seam so both halves meet.
`K.rot180(...)` supplies the partner; `K.s_curve(left_half)` and
`K.seam_half(curve)` create a C2 S-curve `SEAM` point list.
For band-dependent kit pieces, raise `tunic(clear_below=...)` and
`SceptreSpec(visible_to=...)` to the seam, or pass `None` to omit those
cutoffs.
Prefer a negative seam angle or a custom C2 S-curve through the robes: the
default +28° seam can cross the viewer-right attribute fists around
y=404–456. The seam is not drawn.

Contents

1. The one-page recipe
2. The composition plan (write it before any code)
3. Drawing order (the z-stack every court uses)
4. The kit, part by part
5. Pattern fills
6. Faces: the gaze plan and the face kit
7. Colour balance (§C.2): measured levers
8. QA: commands, and how to read what comes back
9. Pitfalls we hit on the K♠, and the fix for each
10. Starting points for the other eleven courts
11. Known limits and open requests

---

## 1. The one-page recipe

1. **Plan.** Fill in the composition table (§2) for your court from its §H
   brief and the §H.0 body geometry. Put the table in the module docstring.
2. **Stack.** In `figure()`, make `sc = K.Scene(rank="K"|"Q"|"J")`, then add
   parts **back to front** in the order of §3: `sc.part(name, part)` for kit
   Parts, `sc.add(name, frag, region)` for anything you build yourself.
3. **Attributes and hands last,** then `K.band_guard(sc, rank)` (Kings and
   Queens), and `return sc` from `figure()`. `build()` is `figure().layers()`.
4. **Preview** with `tools/preview.py` (writes nothing outside your folder):
   look at 750, 1500 (crop), 188 and white, and a 3× face crop, every time.
5. **Read the heal log** (`sc.heal_log`): each entry says what was cut, where,
   and which part it was too close to. More than a handful of entries on a
   face, a hand or an attribute means the geometry needs moving, not healing.
6. **Balance** (§7) only after the drawing is right; then
   `python -m deck.build <ID>` and `python -m deck.qa <ID>`.
7. **Iterate**: at least six render → critique → fix cycles. Critique against
   the Drifters scans in `research/refs/` (`drifters_rpc_drifters-2.jpg`,
   `drifters_dd_03.jpg`): bold contour, flat fills in a few inks, dense small
   patterns, simple confident faces, generous paper.

Everything is authored at final size in card px (750 × 1050, y down), top half
only (art window x 139–611, y 55–511), angles in screen degrees
(0 = +x, 90 = down). Nothing is scaled; nothing paper-coloured is painted;
every width is legal because every mark is a `deck.motifs` Frag mark.

## 2. The composition plan

One row per part, in the brief's words and in numbers. The K♠ plan (from
`art/KS.py`):

| part | colour | geometry (brief) |
|---|---|---|
| crown | gold | Escarpment Crown: band 154–180, five merlons on rays from (375, 700), tops 128 / 105 / 82; jewel r 13, red Ø8.4 core |
| head | paper | egg r 44 about (375, 207): 88 × 113.8, top 163, chin 277 |
| face | ink | 12 strokes; eyes y 213, 24 × 10.1, RULE lids, Ø6 pupils hanging from the lids |
| hair | gold | two lock fans, 4 ribbons (3 current lines) |
| beard | gold | forked, tips (360 / 390, 331), 3 converging current lines per lobe |
| moustache | gold | two drooping leaves (373.5, 242.5) → (345, 259) |
| collar | red | standing fan collar, jade rim, pointed corners (265 / 485, 236) |
| mantle | jade | neckline 270, shoulder corner (182, 330), sides to x 145 at the band; 54 px plain border; strata + one fault (205, 470) → (290, 300) |
| tunic | paper | Spring Lake lens (throat 312, half-width 33); karst voids, Ø10/Ø16 flooded jade |
| lapels | red | on the lens arcs, 68 wide at the waist; rising bubbles knocked out |
| clasp | gold | Lion Mark 40 px, (375, 358) |
| orb | gold | (300, 424) r 33; one free bubble; cup hand |
| sceptre | gold | x 540, 22 wide, seven segments, finial (540, 114) r 29 |
| arms | red | band (222 / 472, 550) → wrists (276, 479) / (498, 455), jade cuffs |

§H.0 body geometry to hit: crown top ≈ 80–100, eye line ≈ 200–215, chin ≈ 280,
shoulders ≈ 330 (x ≈ 180–570), hands 380–480, waist at the band (511).
Frontal heads at x = 375, 3/4 and profile heads at x ≈ 385. Tall attributes
on the viewer's **right** (the pip is top-left: keep ≥ 12 px clear of
x 146–234, y 62–159).

## 3. Drawing order

Painter's order, back to front. Each part hides everything added before it
(geometrically: lines behind stop under its contour, fills behind are trapped
1.6 px under it), and the union of all parts is stroked **once** at CONTOUR,
so every interior edge is automatically MEDIUM (§B.2's 2 : 1).

```
standing collar  ->  mantle / torso  ->  tunic  ->  lapels / trims
long hair (hair_fall)  ->  neck  ->  head (face)  ->  hair cap / hair back
beard  ->  moustache  ->  crown / diadem / cap  ->  clasp (Lion Mark)
sleeves  ->  attributes (sceptre, orb, staff …)  ->  cuffs  ->  one hand5 Part
band_guard (last, Kings and Queens)
```

Rules that fall out of it:

* A **collar that stands behind the head** goes before the mantle: its foot
  hides under the neckline.
* **One hand per half-figure.** It holds the tall attribute on the viewer's
  right. Re-home a secondary object in the clothing without a second hand, or
  omit it. Add the sleeve and tall attribute first, then add the hand.
  `Hand.add_to` tucks the wrist into an arm or cuff already in the scene.
  Alternatively, `hand5(..., sleeve=sleeve)` or
  `hand.with_sleeve(sleeve)` makes the hand and sleeve one Part with one
  outside contour; the cuff is a colour edge, not a second outline.
* **Knockouts near a hand** (lapel bubbles, lining drops, belt nodes, chain
  stones) are whole or hidden, never a paper crescent on the hand's contour:
  `K.clear_of_hand(holes, hand.hand.shape)` fills back the ones that would
  sit on it.
* **Halos** (`halo=K.HALO`, 4.3 px paper channel) only for hands and
  attributes crossing a pattern — e.g. the sceptre over the strata
  (`halo_only=("mantle",)`). **Never** on a beard, moustache or the Lion Mark
  (§G.2: never a halo; on a beard it reads as a bib).
* `sil=False` for anything that should not join the CONTOUR silhouette.

## 4. The kit, part by part

`from deck import courtkit as K`. Every builder returns a `Part(shape, fills,
lines, meta)`: `shape` is the opaque region, `meta` holds anchor points for
the next builder. Full docstrings in the module; the one-liners:

**Geometry.** `arc_sag(p0, p1, s)` arc from chord + sagitta (+ bulges to the
left of travel) · `arc3(p0, pm, p1)` · `arc_c(c, r, a0, a1)` · `Path(p0).line()
.sag().arc3().arc_to().close().d` · `chain(p0, heading, ('fd', L), ('arc', r,
deg))` tangent arcs · `spline(points)` G1 arc spline · `vesica(p0, p1, w)` the
deck's leaf · `egg(c, r, chin_dx)` the face-kit head · `mirror(x)`/`bi(x)`
about x = 375 for d-strings, Frags, Parts and regions.

**Marks.** `line(d, w)` · `seg(p0, p1, w)` · `fill(d_or_region, colour)` ·
`dot(p, d)` · `outline(region, w)` · `hatch_in(region, angle)` (FINE, 7.0
pitch, butt caps) · `clip_in(frag, zone)` / `clip_out(frag, zone)` ·
`atomic(frag, key)` (a motif dropped whole if anything covers part of it —
voids, bubbles, rowels never leave a stray arc).

**Scene.** `Scene(rank=…)` · `.part(name, part, halo=, halo_only=, halo_skip=,
sil=)` · `.add(name, frag, region, …)` · `.compose()` (clip → CONTOUR
silhouette → court clip → **heal**) · `.layers()` · `.heal_log`.
`heal` makes every pair of drawn pieces touch or keep §I.12's paper (3.0
between marks, 4.2 alongside, 2.5 between fills, knockout holes 3 px from
edges), measured the way QA 12 measures; it trims the smaller piece locally
and **logs** each change with the neighbour's role (`near`). An
`UNRESOLVED` entry means QA 12 will fail there.

**Current lines (§G.24).** `current_lines(guide, n, region, side=, edge=,
stagger=)`: 3–5 offsets of one guide at 7.0 px, the first 7.0 inside a MEDIUM
edge / 8.4 inside a CONTOUR edge, each rolling into a Ø6.3 terminal that is
checked against the region edge and every line already placed (a straight
end at a 7 px pitch cannot clear its neighbour; the curl can).

**Face.** `face(center, gaze, sex=, age=, lids=, vestigial=, **FaceSpec
overrides)` → `Face(head, skin, lines, anchors, strokes)`. See §6.

**Hair.** `hair_fall(fc, side, HairSpec)` long lock fans beside the face
(under a crown) · `hair_cap(fc, volume=, hairline=, parting=, n=)` hair over
the skull of a frontal / 3/4 head (under a diadem, cap or bare) ·
`hair_back(fc, volume=, n=, nape_drop=)` the back of a profile or 3/4 head ·
`neck(fc, bottom=)` the neck column (behind the head).

**Beard.** `beard(fc, BeardSpec(style='forked'|'full'|'square', side, bulge,
tip, notch_dy, lines, stagger), mo=moustache)` · `moustache(fc,
MoustacheSpec(root, tip, arch, under))`. Pass the moustache to the beard so
its upper edge tucks under it; the chin stays paper round the mouth.

**Hands (§H.0: one five-finger hand per half-figure).** Use the shared
`K.hand5(at, angle, pose, *, size, hand, view, curl, spread, grip_w,
sleeve=None)` primitive. It returns the existing `Hand` dataclass and builds
one smoothed silhouette from a palm quad and five digit centrelines. All
sizes come from the face (`K.hand_size(fc)`), never from the attribute.

```python
size = K.hand_size(fc)
grip = K.hand5((540, 419), -90, "wrap", size=size,
               hand="R", view="back", grip_w=22, curl=10)
grip.add_to(sc, "handR", halo=0)
```

* `wrap`: `at` is the shaft centre; `angle` is the shaft's up-axis in screen
  degrees (−90 vertical, any angle works). `grip_w` is shaft width. Back and
  palm views share one outline; the thumb leaves the palm side on an open V
  and its short tip sits beside the index tip, never across the finger band.
  Put the shaft in the Scene before the hand; use `halo=0` so its lines run
  under the grip without paper rings.
* `cup`: `at` is the wrist; `angle` points wrist-to-fingers. `grip_w` is the
  orb/chalice rim diameter. Finger tips scallop along the lower rim. Place the
  orb from `hand.hand.meta["object_center"]` when an exact shared anchor is
  useful; it is a rim contact, not a hand drawn over the orb face.
* `rest`, `hold_flat` and `open`: `at` is the wrist and `angle` points toward
  the fingertips. `curl` softly shortens/bends digits; `spread` fans them.
  For `hold_flat`, set `grip_w` to the held object's width and draw that
  object behind the fingers.
* `hand="L"|"R"` is anatomical handedness. `view="back"|"palm"` is the
  visible side. The thumb side follows both, so don't flip the geometry by
  hand. The hand has four tapered fingers with a small knuckle rhythm and one
  opposing thumb; use at most three short MEDIUM inner lines, each beginning
  at least 7.3 px clear of a fingertip notch.
* `hand5(..., sleeve=sleeve)` and `hand.with_sleeve(sleeve)` return a single
  hand+sleeve Part and a shared outer contour; the cuff is only a colour edge.
  Without a pre-composed sleeve, add the sleeve/cuff first and use
  `Hand.add_to(sc, name, halo=0)` to tuck the wrist into it.

The legacy `fist`, `cup`, `flat` and `open_hand` builders remain available so
unmigrated cards retain byte-identical outputs. Do not use them for new court
hands; migrate a card to `hand5` as part of its own court feature.

**Garments.** `mantle(MantleSpec, border=, pattern_kind=, **kw)` bilateral
arc-chain mantle with a plain border band + FINE seam and the house pattern
inside · `torso(neck_y=, neck_hw=, shoulder=(hw, y), side_x=, turn=±1,
colour=, pattern_kind=)` a generic doublet / bodice / tabard, turning with a
3/4 head · `LensSpec` + `tunic()` + `lapel()` the Spring Lake lens front ·
`sleeve(SleeveSpec)` → (sleeve, cuff) · `standing_collar(top_y=, half_w=,
shoulder=, rim=)` a pointed fan collar (never round: no nimbus) ·
`cap(fc, kind='flat'|'hood')`.

**Crowns and regalia.** `crown_band(cx, top, h, hw, bow, v=, edge_deg=)` the
band every crown stands on · `merlon_crown(CrownSpec)` (K♠; re-parameterise
the rays and tops for other merlon crowns) · `diadem(y=, kind='stalactite'|
'point'|'knee'|'bead', n=, lengths=, widths=, fc=face)` circlets that wrap a
frontal or 3/4 head · `jewel(c, r)` small rosette with a red core cut into
the gold · `orb(c, r)` · `sceptre(SceptreSpec)` · `staff(p0, p1, w)` any
plain shaft (trumpet, paddle, key stem, staff).

**Lion Mark.** `lion_clasp(c, 40)` — every court's hallmark (§H.0), solid gold
with an Aquifer contour (legal on red), 9 strokes. Never a halo.

## 5. Pattern fills

`pattern(region, kind, origin=, **kw)` clips a `deck.motifs` pattern to any
region, drawn in Aquifer FINE:

| kind | brief | use |
|---|---|---|
| `strata` | §G.11 (`heights`, `hatched`, `fault=((x,y),(x,y))`) | ♠ mantles, plinths |
| `karst` / `karst_flooded` | §G.12 (`pitch`, `weights`, `flood_min`) | ♠ tunics; flooded = jade caverns |
| `scales` | §G.16 (`r`) | Q♥ bodice, K♥ trim |
| `ashlar` | §G.20 (`block`) | ♦ stonework |
| `fluting` | reed / buttress lines (`pitch`) | ♣ |
| `hatch` | plain 45° | one half of a split shape |
| `rowels` / `rowels_solid` | §G.22 | ♦; `_solid` = gold stars + Aquifer contour (the only legal gold on red) |
| `bubbles` | §G.9 grid | ♥ |

* Give the pattern a **plain border** (`mantle(border=…)`, `torso(border=…)`):
  a FINE seam parallel to the silhouette so no pattern line grazes a sloping
  contour. It is also the cheapest jade in the balance (§7).
* Patterns are **Aquifer on jade/gold/paper** or **knocked out to paper on
  red/jade** (`C.knockout(field_d, frag)`); never gold line on red.
* For a pattern that must read as a jog or a break (the fault), put it where
  the panel is **open**: the K♠ fault only read once it crossed an uncovered
  panel steeply (≈ 63°); at ≈ 22° it ran nearly parallel to the courses and
  vanished under the hands.

## 6. Faces

**Gaze plan (§H.0).** Kings frontal except K♦ (profile left) · Q♠ 3/4 left ·
Q♥ 3/4 right · Q♣ 3/4 left · Q♦ 3/4 right · J♠ profile right · J♥ profile
left · J♣ 3/4 left · J♦ 3/4 right.

**The kit (§H.0), and what `face()` guarantees.**

* Head: the Moss egg, 88 × 113.8 at r 44 (queens: `sex='f'`, r 42).
* Eyes: 24 × 10.1 vesicas — RULE upper lid, FINE lower lid — with a Ø6 pupil
  **hanging from the lid** (the level, heavy-lidded gaze). `lids=` 'heavy' |
  'level' | 'half' | 'lowered' | 'raised' | 'closed' (+ `vestigial=True` for
  the Q♠ dots).
* One MEDIUM brow arc per eye; MEDIUM nose; two-arc lip bow + FINE lower-lip
  tick; optional ear C (`ears=True`). ≤ 14 strokes (`Face.strokes`).
* **Frontal**: one half drawn and mirrored — exactly symmetric.
* **3/4** (`'3/4-left'|'3/4-right'`): features shift 12 % of the head width
  toward the turn, the chin swings (the egg itself turns), the far eye is
  70 % wide and **its outer corner joins the head contour** (the lids run
  0.8 px into the outline: no near-miss, and it reads as the eye turning
  away), the far brow ends on the contour, one nose ridge hooks back, the
  far half of the mouth is foreshortened, the far pupil stays centred.
* **Profile** (`'profile-left'|'profile-right'`, exact mirrors): one G1 biarc
  chain — forehead, brow ridge, nose-root notch, straight ridge, rounded
  tip, lips, chin, throat, neck to the collar, nape, occiput — plus one eye,
  brow, nostril hook and mouth line springing from the contour, ear C and
  jaw line (8 strokes). The head region includes the neck: put the collar in
  front.
* `sex='f'` finer arched brows, shorter nose, smaller mouth; `age='young' |
  'adult' | 'elder'` nudges nose, brow and mouth. Anything else: FaceSpec
  overrides as keywords (`face(..., pupil_dx=2, ears=True)`).

**Face lessons (K♠).** Keep the face at the kit's size and make the hair and
beard smaller rather than the face bigger (a 150 px gold mass round an 88 px
face reads as a mask). A lip bow tucked under a fat moustache gets eaten by
heal: the kit's default moustache sits 8.5 px below the nose base with a
slim lower edge, the mouth 42.5 px below the eye line. The beard's edge must
clear the mouth corners by ≥ 3 px (the kit does this). Never add
cheek/age lines: at this size they read as smiles or scratches.

## 7. Colour balance (§C.2)

Targets over both halves (band excluded): paper 45–50, jade 15–20, red
12–16, gold 10–15, Aquifer ≈ 12 (8–16). QA 5 reports them; only gold ≤ 15 is
a hard check.

**Two facts before you start.**

* The **corner pip is inside the measured window**: 2.4 points of Aquifer
  on every court before you draw a line. The K♠'s own ink is 15.3 %; QA
  reports 17.7. The four minimums (45 + 15 + 12 + 10 = 82) leave the ink
  ≤ 18 — every court will sit near the top of the ink band. Ask the
  director for the pip waiver in writing rather than stripping line work.
* **Ink on a fill subtracts from that fill.** Strata hatch on jade costs
  jade; bubbles knocked out of red cost red and give paper.

**Measured levers on the K♠** (points of the window; your mileage varies with
what overlaps):

| lever | effect |
|---|---|
| raise the mantle's neckline 6 px and flatten its slope 2° | jade +2, paper −2 |
| plain mantle border 38 → 50 px | jade +1.0, ink −0.5 |
| plain border 44 → 54, sceptre 22 → 20 wide, lapel bubbles Ø12.6 → 9.5 | jade +0.5, ink −0.5, gold −0.2 |
| lapels +4 px wide | red +0.2, jade −0.2 |
| standing collar +4 px wider / 4 px taller | red +0.2, paper −0.3 |
| forearms red instead of jade (jade cuffs) | red +1.2, jade −0.5 (and the arms finally read) |
| flood the Ø10 karst voids as well as the Ø16 | jade +0.1 |
| hair 5 → 4 ribbons, beard 4 → 3 lines | gold −0.3, ink −0.1 |

Order of work: get the drawing right; then fix **paper** (shoulder height,
mantle width); then **jade** (plain borders, jade garments that are not
under pattern); then **red** (lapel/collar widths, cuffs, sleeves); gold
last (it is always the easiest: regalia sizes). `K.balance_hint(balance)`
turns a QA balance dict into this list.

## 8. QA

```sh
.venv/bin/python tools/preview.py art/QS.py QS work/<you>/out --qa   # drafts: writes only to your out dir
.venv/bin/python -m deck.build QS          # the real card: cards/QS.svg, build/png/QS.png, build/png/small/QS.png
.venv/bin/python -m deck.qa QS             # rebuilds on both stocks + checklist row; build/qa/report.json, build/qa/flags/QS.png
```

Look at every render (the Read tool on the PNG), and crop:

```sh
magick build/png/QS.png -crop 480x480+135+55 +repage /tmp/top.png             # the top half at 1×
rsvg-convert -w 2250 cards/QS.svg -o /tmp/q3.png                               # 3× for faces
magick /tmp/q3.png -crop 540x600+855+420 +repage /tmp/face.png
```

A court is done when `deck.qa` shows ✓ on 1, 4, 4b, 5, 6, 8, 10a, 10c, 12
(vector), 17, 24, 25 and every `!` has been looked at:

* **12 raster** (`!`): narrow paper wedges where a line meets another at an
  acute angle (hatch into a course line, a current line into an outline).
  Crop each bbox from the report at 6× and confirm. The K♠ keeps 8 such
  wedges (moustache tips, orb latitude into a finger, fault into a course).
* **4c** (`!`): a lower plate under a higher solid. Cut it out (the layer
  trap, ART_CONTRACT §2.1). `flatten_fills` does this within one part.
* **5r** (`!`): thin gold on red — gold on red must be a solid with an
  Aquifer contour (`rowels_solid`, `lion_clasp`).

Also check `sc.heal_log` (and its `near` field) after every change, and that
`build()` is deterministic (two runs, same hash).

## 9. Pitfalls we hit, and the fix

| symptom | cause | fix (now in the kit) |
|---|---|---|
| a fill thinner than HAIRLINE at y 511 | the band clip made a sliver heal never saw | `Scene(rank=…)` clips to the court clip before healing |
| a line 1–2 px above the band rule (QA 12 ✗) | a border seam's bottom edge / a pattern end just above y 511 | mantle border never runs along the bottom; heal runs against the band rule; `sceptre(visible_to=511)` |
| stray '⌣' arcs under a clasp | a karst void half-covered by the clasp | `atomic()`: voids, bubbles and rowels are kept whole or dropped |
| nose ridges trimmed at the top | the two ridges 2.9 px apart at the bridge | `nose_dx_top` 3.7, ridges start 3 px below the eye line |
| lip bow eaten | moustache too fat / too high; beard edge at the mouth corners | moustache root 8.5 below the nose base, slim `under`; mouth lower; beard edge 8 px outside the corners |
| chert vesica touching the fist / the shaft outline | the shaft's CONTOUR, not MEDIUM, sets the free room | `_segment(edge=CONTOUR)`; seat the fist on a collar |
| fingerprint beard, a row of terminal "buttons" | concentric fan lines ending together | converging current lines, `stagger` 13 |
| orb vent read as a smile | a thin FINE ellipse at the pole | no mark at the pole; the bubble floats free, 4.2 px clear |
| orb hand a white slab | wrist almost level with the sphere, or so far below it that the back is longer than the fingers | `cup` fingers from 1.14 r to ≈ 0.45 r, wrist ≈ 1.3–1.5 r below the centre (move the cuff up), tapered back |
| thumb laid over the finger band; cup reads as a hand over the orb; doubled cuff outline | stacked thumb construction, upright cup fingers, sleeve and hand outlined separately | use one `hand5` silhouette: an open V web from the palm side, rim-following cup tips, and one shared hand+sleeve contour |
| red forearms merging with red lapels | same colour touching | route the arms over the jade panels, jade cuffs |
| jade arms invisible on a jade mantle | no contrast | red arms (or plain arms on a patterned panel) |
| the Lion Mark reading as a sheep / owl / bat / horned mask | round fleece scallops with droopy wing tufts; raised wings at 40 px | level wings with stepped primaries behind a scalloped mane; paper face; every face mark touches the gold rim |
| 3/4 far eye cut by the contour; far pupil deleted | features slid over a symmetric egg | the egg turns (chin swing); the far eye joins the contour; far pupil centred |
| diadem points crowding into a zigzag | kites wider than their pitch | `diadem` clamps widths to pitch − 3 − MEDIUM; use n ≤ 7 on a head |
| a tiny dot left on a brow | heal trim left a crumb | heal drops crumbs shorter than max(2.5, 1.5 w) |
| `NameError` / odd failure inside deck.motifs | Track B mid-edit | re-read the source, wait, retry — never patch motifs from a court |

## 10. Starting points for the other eleven

These are the kit calls the K♠ work and the kit test busts
(`work/ks-panel/final/test_heads.py` → `work/ks-panel/final/out/test-heads.png`)
have exercised; everything else is parameters.

| court | head | hair / headwear | body | hands / attributes |
|---|---|---|---|---|
| Q♠ | `face(…, '3/4-left', sex='f', lids='closed', vestigial=True)` | `hair_fall` behind + `hair_cap`; `diadem(kind='stalactite', n=5–7, fc=)` | `standing_collar` (ruff) behind `torso(turn=-1)`; `gill_plume` ×6 on the ruff | one `hand5("hold_flat")` on the mirror frame; re-home the laurel |
| J♠ | `face(…, 'profile-right', age='young', lids='raised')` | `cap(kind='hood')` + `lion_clasp(…, 40)` badge | `torso(turn=+1, pattern_kind=…)` | one `hand5("wrap")` on the lantern chain |
| K♥, K♣ | frontal, `age='elder'` | `crown_band` + merlons re-parameterised / `diadem(kind='knee')` | `mantle` + `lapel`/`tunic` or `torso` | one `hand5("wrap")` on the tall attribute; re-home or drop the orb |
| K♦ | `'profile-left'`, `age='elder'` | `hair_back` + beard adapted to profile | `torso(turn=-1)` | one `hand5("wrap")` on the key/staff |
| Q♥ Q♣ Q♦ | 3/4, `sex='f'` | `hair_cap` + `hair_fall`; `diadem(kind='point'|'bead')` | `torso(turn=±1, pattern_kind='scales'|…)` | one `hand5("cup")` for a rim or `hand5("wrap")` for a stem |
| J♥ | `'profile-left'`, young | `hair_back` | `torso(turn=-1)` | one `hand5("wrap")` on the fiddle neck; re-home the bow |
| J♣ J♦ | 3/4, young | `hair_cap(parting=…)` + `cap(kind='flat')` | `torso(turn=±1, pattern_kind='rowels_solid'…)` | one `hand5("wrap")` on the tall attribute |

Keep the K♠ conventions: CONTOUR silhouette, MEDIUM interiors, FINE patterns;
gold only on regalia and hair; paper halos only on hands and attributes; the
Lion Mark (40 px) on every court; patterns on plain-bordered panels.

## 11. Known limits and open requests

* **Ink includes the corner pip** (2.4 points): ask for the §C.2 waiver
  (K♠: figure 15.3 %, reported 17.7 %).
* **Lion Mark at 40 px** is a hallmark, not a portrait: the face is a V brow,
  a nose and the muzzle arcs; the wings are level. `deck.motifs.lion_mark`
  (the 50–60 px mark) reads as a bat at 40 px on red and its face does not
  survive §I.12 at that size — Track B could adopt `lion_clasp`'s level wings
  for small sizes.
* **Profiles**: the head region includes a neck down to `mouth_y + 62`; a
  bare profile (no collar in front) shows a sock-like neck.
* **3/4 hair**: `hair_cap` + `hair_fall` are frontal constructions shifted
  for the turn; long 3/4 hair wants a near-side fall wider than the far one
  (pass different `HairSpec`s per side).
* The test busts' torsos are plain pentagons (`torso`): real courts dress them
  with lapels, trims and patterns as the K♠ does.
