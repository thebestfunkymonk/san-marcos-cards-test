# JS (J♠ The Lantern Page) — progress log

## 2026-09-23 session start
- No prior progress file. Found art/JS.py broken: JS.py used `hg.outer` but the mid-rewrite
  art/_js_hood.py HoodGeo only keeps `shape` / `shape_nocrest` (outer is a local).
- Plan: repair (use hg.shape), render, write build/review/JS-critique.md, then rework.
- Draft outputs go to scratchpad (not the repo).

## iteration log (session 1)
- Repaired JS.py (hood `outer` → `shape`); rendered; wrote build/review/JS-critique.md.
- REWROTE: _js_hood.py (explicit spline hood/cape runs, stepped jade crest with strata courses,
  ribbon `lock()` builder, concave stalactite dags, hood_part ornament option), _js_lantern.py
  (bigger lantern, salamander bail redesigned: head up at left, ccw coil, legs, flecks, no gills;
  chain with face/edge links hooked through the ring hole), _js_garment.py (sleeve_part, livery
  collar of graduated gold beads), _js_util.py (spline_region/open_spline/region_of/ribbon2).
- JS.py composition: head (384,208) r42.5; hood+cape to x168–594; livery collar + Lion Mark at
  (398,334); jade puff sleeves to the band; chevron doublet; gold belt 464–498; rope coil over the
  left shoulder with red forearm/jade cuff; lantern LX 523 with red forearm rising from the right
  (wrist 565,199), fist 180 holding the chain.
- Balance at v5: paper 50.9 jade 13.7 red 11.8 gold 6.8 ink 16.8. QA 4c/12 still to fix.
- NEXT: full critique round 2 (doublet pattern calmer, left sleeve sliver, crest, locks, gold),
  then QA cleanup (4c at brim 407,165; 12 raster).
- v15: rope coil rewritten (3 turns, MEDIUM divisions, FINE lay ticks staggered half a pitch between
  turns, greedy spacing) — reads as a coil and heals cleanly; lining now covers the rim edge (no red
  slivers); salamander/hood outlines simplified (compose 107 s → 7 s); heal log 250 → 72.
  Left cuff red (a jade cuff merged with the jade doublet); right forearm base pulled in from the frame.
- v22+: doublet = Λ chevron rows knocked out, plain placket with 2 gold buttons, right half stepped one
  course (the fault); livery collar of graduated gold pearls (Ø8.4–11.6 alternating Ø6.3) with the
  Lion Mark at (398,326); shoulders raised 12 px, hem 13 sag / 33 dags; lantern R58, frame lines drawn
  as a disjoint partition (no doubled outlines); crest hatches its middle course; lining stops 7 px
  short of the brim. deck.build JS (both stocks) + deck.qa JS: all hard ✓, 4c ✓, 12 raster ! (8 wedges).
  Balance: paper 49.2 jade 14.5 red 11.6 gold 7.5 ink 17.1.
- NEXT: eyeball the 8 raster wedges (build/qa/flags/JS.png); polish passes (face, hood back, gold).
- v27: livery skips beads within a CONTOUR half-width of the coil/lantern/forearm (no paper holes);
  lining 12, dags 36, chevron pitch 25, right cuff 13; salamander legs (0.09, 0.40) with paddle feet;
  page_profile gains a `nostril` parameter (JH-style hook now visible under the nose).
- v28/final candidate: crest steps 13 px (treads 139/126/113); code cleanup (removed unused powder,
  slash, pierced-pane, drip/fringe options and util helpers; ribbon2 → ribbon); docstrings refreshed.
  deck.build JS both stocks + deck.qa JS: 13 pass, 0 fail, 1 warn (12 raster wedges: salamander
  legs/collar, roof rib/hatch, coil/dag — looked at, acceptable). Deterministic build.
- NEXT: final look at build/png/JS.png, 188, white; append resolution to JS-critique.md.
- DONE: critique resolution appended to build/review/JS-critique.md. Final QA row: 13 pass, 0 fail,
  1 warn (12 raster). Files: art/JS.py, art/_js_{face,hood,lantern,rope,garment,util}.py.
