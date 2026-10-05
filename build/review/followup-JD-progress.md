# followup-JD progress (art director's note: trumpet + tooled scroll)

## 0. Start
- Note: (1) trumpet reads as a short fat funnel/megaphone -> long straight herald's trumpet, longer tube, modest
  bell, bell near (590,150), banner still hangs from it; (2) belt tooled scroll = tiny squiggles -> fewer, larger,
  regular volutes of tangent arcs, one vesica leaf per turn (§G.31).
- Files: art/JD.py, art/_jd_parts.py only. Drafts -> scratchpad/jdf/vN.

## 1. Trumpet (v1–v5, v16–v25; drafts scratchpad/jdf/vN)
- Mouth (584,124), axis -63, bell 48 long / mouth hw 22.5, flare exp 2.8 (a trumpet flare, not a cone), tube 18
  (was 24), knop at the bell's end; banner rod lashed at s=88 -> ~40 px of plain tube shows above the banner.
  Bell centroid ~(577,146) (brief: ~590,150; the frame clip at x 610 stops it going further right).
- Banner 110 x 90 (74 left / 36 right of the rod crossing so the tube exits the bottom edge clear of the corner),
  lion 60 (raised 3.4 so its ripple keeps 4.2 off the seam), fringe (10.5, 9.5, 13) starting right of the tube
  with its own sine; drips shortened (not dropped) near the tabard/tube.
- Mouth: small bell cannot hold a 3 px gold rim inside its contour (heal ate the throat -> paper lens) ->
  throat_merge: the whole mouth ellipse dark (cut out of the gold, no 4c), split line springs from it.
- Lash knop removed (it made a gold sliver above the rod); boss moved to s=240 (was on the tabard contour);
  lower ferrule removed (made a gap wedge under the fist).
## 2. Belt tooled scroll (v6–v15)
- New J.running_scroll: ONE row of eye volutes (r0 8.6) on a running stem of tangent arcs (CCW quarter up,
  CW half over, CCW quarter down to a base line), lambda fork at each right foot (eye half turn r0/2 -> Ø6.3
  terminal), one sessile vesica leaf (17.2 x 6.4) standing between each two volutes. Belt 441-473 (32 tall).
  Old motif at height 22 had r0 6.2 and heal chopped it (27 heal entries) = the "handwriting".
- Window between buckle and cuff: buckle 38 wide (was 42), WR -> (489,421.5) so 2 whole volutes + 1 leaf show.
- Cuffs: gauntlet(sprig=...) = one unit of the same scroll (stem, eye volute, leaf); left cuff's sprig sits
  under the band (only a gold corner shows).
- v25: QA all ✓ in preview; balance jade 14.6 gold 7.8 (was 14.9 / 8.3) — thinner trumpet costs gold.

## 3. FINAL — DONE
- Docstrings updated (JD.py table: trumpet, banner, belt, cuffs; _jd_parts header).
- deck.build JD (limestone + white), deck.qa JD: 14 pass, 0 fail, 0 warn; gold 7.8%.
  Balance ink 14.8 gold 7.8 red 15.1 jade 14.6 paper 47.7. build() deterministic (same hash twice).
- Review crops: build/review/followup-JD-trumpet-3x.png, build/review/followup-JD-belt-3x.png.
