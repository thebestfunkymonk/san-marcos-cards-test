# corr-AS progress (A♠ alignment correction)

## iter 0 — baseline (before any change)
- Backup: build/review/AS.py.bak-before-corr (art/AS.py as found).
- Measured (render w/o index + stock, alpha>0.05): bbox x 108–642, y 140–735, middle y 437.5, alpha centroid (374.9, 363.1).
- Other aces: AH mid 558 / AC 552 / AD 495.5.

## iter 1 — drafts (scratchpad corrAS/out_A|B|C)
- Legend ink: L1 559.6–590.4, L2 612.9–625.1 (cx 375.20), L3 645.8–660.2 (cx 375.22), arc 698.9–735.0 (ends x 208.4/541.6 = L3 em-rule ends 208.2/542.2).
- Ink gaps: plinth→L1 45.6, L1→L2 22.5, L2→L3 20.7, L3→arc ends 38.7 / arc centre ~62 → line 4 floats apart.
- A: dy 84, legend as brief (mid 521.5). B: dy 92, arc lowest 718.4, L2/L3 centred on ink (mid 521.5). C: dy 88, arc 726.
- Choice: B rule — arc END baselines on the legend's 35 px pitch (695) → lowest 718.6; L3→arc-centre gap ≈ plinth→L1 gap (≈45). dy 92.
- Columns (253–482 = lion head 260 → plinth top 483), waterline (symmetric, 14.8 px off silhouette), emblem cx 375.0: keep.

## iter 2 — applied (FINAL)
- art/AS.py: COMPOSITION_DY = 92; build() translates the spade path (G.translate) and the whole gold Frag (.translate) — path data, no SVG transform, nothing redrawn.
- art/_as_legend.py: arc_row() sets line 4 lowest_y so the arc's end baselines sit one 35 px pitch under line 3 (735 -> 718.6, legend coords); straight lines + em-rules centred on their ink (L2/L3 were +0.2 px).
- Built limestone + white. Rendered block x 108–642, y 232–811, middle (375.0, 521.5) (vector 232.0–810.6, mid 521.3). Centroid (374.9, 454.8).
- Gaps: plinth→L1 45.6, L1→L2 22.5, L2→L3 20.7, L3→arc ends 22.3, L3→arc dip ≈45.4.
- Clearances: TL index 106.8 (left column), BR index 107.7 (L2 em-rule), arc→BR 107.9, right column→BR 237.1. Safe margins L 70.4 R 70.5 T 194.5 B 201.9.
- QA AS: 11 pass, 0 fail, 1 warn ([12] gold raster 12 narrow-gap regions inside the emblem — identical to baseline, pre-existing). 10c min_clear 106.85.
- Renders: build/review/corr-AS-after-750.png, corr-AS-before-after.png, corr-AS-legend-3x.png, corr-AS-columns-3x.png, corr-AS-waterline-3x.png, corr-AS-188-before-after-white.png.
- Contract note for orchestrator: ART_CONTRACT §3.2/§10 should record the A♠ shift (+92; spade top 232) and arc lowest 718.6 (+92 = 810.6 on card).
