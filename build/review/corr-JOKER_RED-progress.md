# corr-JOKER_RED progress (client corrections: alignment + Fool's crown/collar)

## Iteration 0 — baseline (before any change; frames already lowered by JOKER_DY 72)
- Originals backed up to scratchpad jr/orig/.
- Measured (render without index/stock, alpha > 0.1): figure bbox x 166.5–561.0, y 124.5–627.5; figure alpha centroid (358.7, 327.6); caption (rule/title/subline) y 758.5–857.5.
  Figure-to-rule gap 134.5 px; block (fig top..subline 857) middle y 490.8; bbox middle x 363.8.
- Collar problems confirmed on a 3x crop: dags crowded into a narrow paper channel, first dag/band clipped by the ear, uneven fan, scalloped ground.
- Plan: (1) rewrite collar as a circular-arc band + 5 equal dags on its normals (regular fan) + round bells with a slit, paper ground = uniform 4.2 offset, ear/leg over the band with 4.2 interlace gaps; (2) translate figure group (pig, ring, bubbles, scroll) by (DX, DY) and place ripples separately.

## Iteration 1-2 — drafts in scratchpad jr/draft (art/ untouched so far)
- Collar rewritten (_joker_red_pig.py collar_frame/collar_band/collar_dags/collar_over/collar; params in _joker_red_pose.py):
  arc band R 140 (centre on body side), W 7; 5 isosceles dags pitch 20 (8.2 deg fan each), base 18, bell centre 22 beyond band edge;
  bells Ø11.5 with a Ø4.2 mouth hole offset 0.5; ground = gold outline offset 4.2; ear crosses band only (gap 4.2 from its visible red);
  ventral end runs to the near/far foreleg outline (the near foreleg's front edge is invisible in the red, so ending there read as a broken stub).
  Bell-to-bell red bridges 3.7, to ear KO line 4.4, to leg KO line 3.9 (all >= 3.1; enforced by a ValueError in collar()).
  Lesson: a fan centred on the head axis runs into the ear; the channel between ear and foreleg runs ~62 deg, so the fan axis = HEAD +9 deg.
- Placement: FIG_SHIFT (+15, +64) rigid translate of pig/ring/rivets/bubbles/scroll; ripples separately at RIPPLE_C (450, 688.5).
  Result: figure y 188.5–712.0, gap to rule 50.0, block middle 522.8; bbox mid x 378.5, alpha centroid x 373.4, darkness-weighted centroid x 370.1.
- preview --qa: all hard checks pass.

## Iteration 3 — final (installed in art/, built, QA)
- DAG_BASE 18 -> 16 (each dag reads as its own isosceles point; band shows 4 px between them). Ripples x 455 -> 450.
- Installed art/JOKER_RED.py, art/_joker_red_pig.py, art/_joker_red_pose.py, art/_joker_red_water.py (only these).
- Built JOKER_RED on limestone and white; `deck.qa JOKER_RED`: 12 pass, 0 fail, 0 warn.
- Final: figure x 181.5–575.5, y 188.5–712.0; gap to rule 50.0; block (188.5–857.5) middle 523.0; bbox mid x 378.5;
  alpha centroid (373.3, 392.2); darkness-weighted centroid x 370.1. Collar gold-to-red min 4.19 px (was 3.59).
- Renders: build/review/corr-JOKER_RED-{before,after}-750.png, -before-after-axes.png, -collar-before-after-3x.png,
  -collar-after-3x(-rotated).png, -collar-ear-6x.png, -collar-ventral-6x.png, -after-188-x3.png, -after-white-750.png.
- For ART_CONTRACT §10 (not edited, outside ownership): porthole centre now (390, 394) (brief 375,330 + JOKER_DY -> 375,402); ripples centre (450, 688.5).
