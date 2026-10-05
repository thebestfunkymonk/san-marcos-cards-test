# courts-mix progress (J♣ / K♥ / Q♥ polish)

Work dir: work/courts-mix/ (baseline renders in work/courts-mix/base/).

## 0 — baseline (fresh start)
- preview --qa baseline: JC 12 ✗ vector 2.85<3 at (392.5,214.6) + 4c jade under gold [306,872,425,889]/[324.7,161,444,177.7] (cap hatband);
  KH 4c red under ink [143,488,147,497] + red 2 thin raster; QH 4c jade under ink [588,314,593,321], [327,137,335.7,149.7].
- balance: JC paper 53 jade 11.7 gold 5.5; KH paper 44.9 gold 9.9; QH gold 8.7 ink 16.7.
- next: fix QA items, then critique.

## 1 — JC QA + face + balance (art/JC.py, _jc_parts.py, _jc_head.py, _jc_body.py, _jc_paddle.py)
- cap: jade cut under the gold hatband now opens through the contour (heal had refilled the 0.2 px-from-edge hole → 4c). 4c clear.
- face: switched to kit K.face('3/4-left', young, raised, pupil_dx -3) (J♦'s hand mirrored) → younger; vector 12 (pupil 2.85 px) gone.
- added far-side gold lock (H.far_lock, pageboy mirrored) framing the face; neck 40→33.
- paddle3(blade_color=JADE): split-tone blade (plain half jade, other half hatched paper). ladder_guard(color=GOLD): gold braid guards.
- guard_stop(): upper guards end square at the husk buckle (5r thin gold on red cleared). buttons moved onto vee midline (372/396) — 2nd button outline was broken.
- balance now paper ~49.6 jade 13.3 red 13.9 gold 7.0 ink 16.2. Next: JC critique (collar hem, plume root raster gap, belt hand), then KH.

## 2 — KH QA + window (art/KH.py, _kh_parts.py, _kh_window.py)
- 4c red-under-ink at the left edge: left sleeve base 162→176 (its outer edge no longer crosses the robe edge at a shallow angle above the band).
- thin red at the band: robe ripple knockouts clipped 5.6 px above y 511.
- pearls: bead_off 10.6→11.4, keep inset 3+FINE/2 and above the band, avoid = blockers+4.75 → no more heal-clipped 'C' pearls.
- chalice: 8-spoke vent roundel read as a ship's wheel (sailor kitsch) → §G.1 crater (6 curved ribs) sized to the bowl circle; bowl_h 44, stem 66 (fist no longer crushed).
- window: h 112 (WIN_C y 432), fins without spines, outlined eelgrass ribbons rising at left, whole 3-ring vent boil at right (ring gaps 3.3 so heal keeps them).
- tried a pole halo: messy against the ripple knockouts → reverted. Balance: paper 45.3 jade 14.5 red 14.3 gold 10.1 ink 15.8.
- remaining raster wedges (scale lattice into outlines, window frame × lapel edge): acceptable acute wedges. Next: QH.

## 3 — QH (partial, recovered by retry from diff vs work/courts-mix/orig; not logged by the interrupted attempt)
- QH.py: cap moved back on the head CAP_C (362,194) R 62; petals = ONE ring of 8 long vesica petals (rib + half hatch, snap_to_limb), pearl d20;
  pearls gap=3.4; front lock shifted left 6; leaf/petiole raised (568,262), notch.
- _qh_cap.py: added radial_petals() + snap_to_limb(); _qh_attr.py: leaf jade fill pulled back from sharp lobe tips (4c).
- experiments in work/courts-mix/q1..q32 (qhv.sh override harness). Retry resumes: verify QH QA + look, then critiques.

## 4 — QH cap redesign as a flat rosette (retry session)
- sphere-projected petals (any params, q1–q32) still read as helmet/beanie at 1×. New v6: CP.leaf_petal / CP.rosette
  (screen-space vesica petals, pinwheel lap so each shows its hatched half), 9 petals round the pearl (d22) at
  angles -70..250 step 40, dome ((362,168),62,60), pole (360,136); gold rim IN FRONT (petals tuck under, dome to rim
  bottom, rim cut square at x 418); base inset under petals (core 16) and clipped to the petal hull. QH.py ROSETTE dict.
- leaf: PETIOLE/LEAF dicts; petiole w7 to (566,268), notch (13,22), leaf jade fill opened 3.3 (lobe tips) → 4c clean.
- QH preview QA (work/courts-mix/v33): 4c ✓, 12 vector ✓ (raster warns: acute wedges), balance paper 46.4 jade 16.0 red 12.5 gold 8.4 ink 16.7.
- next: KH window/staff polish, JC critique items, critique file, then deck.build + deck.qa for JC KH QH.

## 5 — KH window + pole polish
- KH.py: WIN_KW / POLE_KW module dicts (harness work/courts-mix/kh_try.py + khc.sh).
- window: eelgrass = two SOLID paper blades (hw 2.8) swaying right (outlined pairs read as prongs); vent boil = three
  flat rings rising into view from the bed at the right (rip_c (24,5), ry 6/13.2/20.4, aspect .5) — whole rings read as a target.
- pole: _kh_parts.pole() gains band_n + wraps (spiral cord grip, MEDIUM, pitch 8, slant 7); KH bindings at 84/352 + grip wrap 378–426.
- tried lapel_w 50 for jade: +0.1 jade, +0.3 ink → reverted. KH preview QA (k17): 4c ✓ 5r ✓ 12 vector ✓; balance paper 45.1 jade 14.7 red 14.3 gold 10.1 ink 15.8.
- next: JC critique/fixes, critique file, final builds.

## 6 — JC balance touch (retry session)
- JC.py: near pageboy outer pushed out ~6 px and far lock ~5 px (fuller bob; gold 7.0 → 7.6), left puffed sleeve
  outer edge out ~6 px (jade 13.3 → 13.7). Preview QA (work/courts-mix/j2): all ✓, balance paper 48.6 jade 13.7 red 13.9 gold 7.6 ink 16.2.
- face: kept the kit 3/4-left young face (J♦ mirrored) from step 1 — checked vs J♦ at 4×: same hand.
- deck.build JC KH QH (both stocks) + deck.qa run once after steps 4–5: all hard checks ✓ (KH/QH 12 raster warns = acute wedges).
- next: write build/review/courts-mix-critique.md, rebuild JC, final deck.qa.

## 7 — DONE (final)
- critique written: build/review/courts-mix-critique.md.
- final deck.build JC KH QH (ivory + white) and deck.qa JC KH QH: 40 pass, 0 fail, 2 warn (KH/QH 12 raster acute wedges).
  Balance: JC 48.6/13.7/13.9/7.6/16.2 · KH 45.0/14.7/14.3/10.0/16.0 · QH 46.4/16.0/12.5/8.4/16.7 (paper/jade/red/gold/ink).
- build() is deterministic for all three (two runs, same hash).
