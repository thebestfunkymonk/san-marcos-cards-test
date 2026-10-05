# JOKER_RED progress log

## 1. Start (fresh attempt)
- No prior progress file. Read brief §H.17/§F.4/§C/§I, ART_CONTRACT, current art/JOKER_RED.py, _joker_red_pig.py, _joker_red_water.py.
- Diagnosis of check 24 (151 Limestone px on white): NOT a paper fill. Gold (#B08D57) anti-aliased at 15-17 % coverage on white = (242,237,228) ~ Limestone within +-3. The aces with gold keylines fail the same way (112-182 px). Fix = less gold edge length (threshold 78 px), e.g. move non-brief gold (ripples / wave scroll) to red or shorten; brief only mandates gold for ring, rivets, bubbles, collar.
- Plan: redraw pig from scratch in a new module art/_joker_red_pig.py (arc-built), keep ring/water structure.

## 2. New pig module (iterations 1-5)
- Old modules backed up only in session scratchpad (project is not a git repo).
- art/_joker_red_pig.py rewritten: TORSO closed arc-chain (head+barrel), capsule legs (joint circles + tangents, filleted),
  trotter(cor, h, sole) with cleft + half-hatched sole claw, leaf ear (2 arcs) half-hatched, collar band with 5 dags hanging
  toward the head (DAG_FOCUS<0) + bell rings, P() = scale S + dive bend BEND_R.
- JOKER_RED.py: AXIS_TILT -16 (snout lower-RIGHT, back faces upper-right = natural pitch, belly/legs left), SNOUT_DIST 245, PERP -6.
- Findings: forelegs reaching along the jaw read as a diver's arms (good); body interior too empty; hind legs read as a waving arm;
  water module still positioned for the old orientation (scroll overlaps ring) -> must redo.
- Next: slimmer torso + belly sag, elbow/ham modelling lines, hind legs, tail, water re-layout, QA.

## 3. Composition found (iterations 6-10)
- "Breaking the frame": pig S=0.95 mostly INSIDE the porthole; snout (and fore trotters) out below the lower rim, rump/tail/hind
  trotters out above the upper rim (ring in front of hindquarters). AXIS_TILT -12, SNOUT_DIST 195, PERP -8, BEND_R 1200.
- Legs are heraldic-bent capsule chains (forearm down-forward, cannon forward; hind legs trail).
- Water rewritten: bubbles leave the tail's curl (heading TRAIL_H0) on a biarc that meets a circle R=190 concentric with the
  ring; the scroll (wave_hook copies, outward, clockwise) runs on that circle to SCROLL_END=8 deg + terminal. Ripples at y 603.
- Check 24 analysis: gold AA at ~16 % coverage on white == Limestone +-3. Ring alone (MEDIUM+FINE circles + 16 rivets)
  = 103 such px (> 78 limit) -> check 24 cannot pass with the brief's gold double ring; report as QA false positive.
- QA 12 currently: detail lines ending 0.5-2 px short of contours (make them overlap), eye dot vs lid, ripples 3.6<4.2.

## 4. Iterations 11-18 (legs, collar, ear, tail, placement)
- Forelegs moved down/back so they leave the chest below the throat (no chin knob): FORE_NEAR [(200,44,33),(186,84,24),(132,100,14.5),(98,102,12.5)], ARMPIT_R 5.
- Ear now streams back OUTSIDE the dorsal line (EAR top (96,-46) bottom (114,-40) tip (176,-96)) so the collar band (COLLAR_X 150) is free:
  5 dags + bells hang toward the head, trimmed to stay >= GAP+1 inside the neck contour and clear of the ear.
- Tail: TAIL turns ((10,None),(30,-25),(12,200),(8,150)) a '?'-curl rising from behind the rim.
- Hind legs as a pair trailing up (HIND_FAR offset), both trotters peek above the upper rim.
- SNOUT_DIST 206: rump cap arcs above the rim (reads as hindquarters behind the rim); head out below. Trotters break the lower-left rim.
- water: scroll start = max(after bubbles, where trail meets circle) (no longer raises).
- Next: body modelling lines, remaining QA 12 (ear tip vs head contour), 3x crops.

## 5. Iterations 19-23 (collar/ear junction, forelegs, QA 12 clean)
- Collar band edges now END ON the neck silhouette (torso polygon), silhouette unbroken; band tilted (bottom forward);
  only interior detail lines are cut by dags/bells. COLLAR_X 160. Ear fold runs base-mid -> tip (hatch ends on drawn lines).
- Brisket opening (BRISKET_R 6) + foreleg elbow circle moved inside the torso -> clean V between throat and foreleg:
  FORE_NEAR [(206,40,30),(194,74,22),(166,99,17),(134,104,13.5),(100,106,12.5)], legs have mid circles (muscle taper).
- Draft QA (tools/preview --qa): 12 PASS; only 24 fails (gold AA, see section 3).
- Next: longer shoulder/ham modelling arcs, final polish, deck.build both stocks, deck.qa.

## 6. Iterations 24-29
- S=1.0, SNOUT_DIST 216, PERP -16 (ripples nearer the card axis).
- Ear hatch via hatch_on(): only hatch lines with both ends on drawn lines (contour/fold); fold stops at 84 % (no wedge at tip).
- Trotters pointed (HOOF_L 29, tapered wall), read as hooves.
- Far foreleg splays below the near one (FORE_FAR [(208,42,28),(196,76,18),(176,110,15.5),(156,128,13),(128,140,12)]):
  clean V, no sliver; its trotter breaks the ring's lower-left rim.
- Draft QA: 12 PASS, 10c PASS. Next: deck.build both stocks + deck.qa, then polish ham junction/tail/elbow line.

## 7. Iterations 30-32
- Longer SHOULDER arc (upper arm) and HAM arc; broader pig ear EAR tip (170,-102), up_sag 18.
- Docstrings rewritten for the new design (JOKER_RED.py documents the check-24 finding); dead helpers removed.
- deck.build (both stocks) + deck.qa JOKER_RED: all checks pass except 24 (gold AA; emptying the gold layer -> 0 px).

## 8. Iterations 33-35
- BEND_R 850 (stronger dive arc; head points straight at the ripples).
- FAR_EAR added (ear(e) takes a param dict): far ear peeps past the near one along the back line
  (top (100,-52), bottom (124,-46), tip (200,-106)); outline only (its visible part is a sliver).
- Draft QA: 12 PASS (no raster warnings), 10c PASS.

## 9. Iterations 36-40 (cleanup)
- JOKER_RED.build: after the ring-face cut, contour pieces (CONTOUR_ROLES) shorter than 16 px are dropped (removed a
  stray hind-leg stub inside the upper rim); other red pieces keep the old 5 px sliver cleanup (wrinkles/hatch kept).
- Draft QA 12 PASS, 10c PASS.

## 10. FINAL (iteration 41)
- Hind legs trail along the dive arc (HIND_NEAR ... (416,38,13); HIND_FAR ... (404,72,12.5)).
- deck.build JOKER_RED (limestone + white) and deck.qa JOKER_RED: 11 pass, 1 fail = check 24 (140 px), which is gold
  anti-aliasing, not paint: white SVG holds no #F4EFE3; emptying the gold layer -> 0 px. Breakdown (white, 750 px):
  ring rims 52, rivets 7, collar 24, bubbles+scroll 25, ripples 31, rule 0. Brief-mandated gold alone (ring+rivets+
  collar+bubbles) ~ 90 > 78 limit, so 24 cannot pass without a QA change (e.g. ignore pixels adjacent to gold coverage).
- Status: DONE unless the director wants the check-24 policy changed.
