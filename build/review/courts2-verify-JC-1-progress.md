# courts2-verify-JC-1 (adversarial verify of JC, fixer iter 1-4)
- cards/JC.svg sha1 f2e0dac8 == sandbox rebuild (tools/preview.py) == final/ copy; deck.qa JC 14 pass/0 fail/0 warn (qa rebuilt JC both stocks, same sha).
- pixel diff before/after (top half, 3x): changes only at fist+right forearm, belt hand+left forearm/cuff, reed belt, plume, near hair, pupils. No unexpected changes.
- Audit items: belt-hand thumb/index fusion FIXED; thumb stiff/parallel FIXED (46 deg web V + crease); root bulge FIXED; size 46->58 (audit target met, still ~64% of ~91 px face); fist thumb/line fusion, heel-across-loom, nick FIXED (kit); cuff/loom collision FIXED (cuff ~12 px clear); reed hook FIXED; jade forearm read IMPROVED (spray); gaze FIXED (pupils hang).
- NEW: belt-hand thumb top contour (y 428.6, x 282-298) runs 2 px above and parallel to the belt top edge (y 430.9-431.6, x 302-342), which emerges from the thumb tip at ~(302,430): tangency visible at 750 and in the 180 copy. Crops: TANGENCY_thumb_beltTop_3x.png, TANGENCY_thumb_beltTop_750x6.png, thumbbelt_before-after_8x.png.
- minor: wrist fills the full cuff (no taper), reed now an isolated o-o link, plume inner vane line cut to ~13 px tadpole, cuff/belt/forearm convergence ~6 px at (491-493,423-429), J♦ twin pupils now differ.
- verdict: pass=false (new tangency at the belt hand).
