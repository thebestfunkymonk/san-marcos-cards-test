# v3-hands-review progress
## iter 1 — adversarial review done
- scratch: build/review/v3-hands-review/ (render.py 6x cells → cells/, zoom.py tight 8–14x → zoom/, courts_check.py)
- structure: every specimen hand = 1 polygon, 0 holes, thumb merged (meta). 12 courts' figure() run OK in memory, 0 HandWarnings.
- verdict: FAIL — grip palm view reads stacked (closed finger block), thumb cap still sits on top, horizontal-axis grip/pinch broken, cup reads as hand over the orb face, open-hand thumbs are hooks/pegs, flat-bottomed little finger, line-cap beads at notches, outline spurs at fingertips.

## iter 2 — re-review of round 2 (sec7 round-2 state, specimen 14:17)
- scratch: render_r2.py → cells_r2/ (80 cells 6x), zoom_r2.py → zoom_r2/, rows_r2/ (montages, court crops).
- incident: ran `splice.py --help` (script has no argparse → executed the splice). Verified no change: same size 200825 B, bytecode identical to the 14:16 .pyc; mtime restored to 14:00:52.
- structure: 80/80 hands = 1 polygon, 0 holes, thumb merged; strokes {3.1, 6.25, 2.1}; no text/scale/gradient/filter.
- verdict: FAIL. Pass: back-view open hands spread (row 10), sleeve merge (row 12), diagonal grips 02_00/02_04. Fail: palm-view grip (5 parallel bands), thumb-up hump on back grip, thumb='behind' tab, horizontal grips (02_02/03/06/07), pinch (thumb stacked parallel on index, pointing-finger read), cup (drip fingers), open together/curled (chopped little finger, notch spurs, peg/horn thumbs, floating life-line), courts KS/KC orb hands flat on orb face, paper halos KS/KC staffs + JD mace.
