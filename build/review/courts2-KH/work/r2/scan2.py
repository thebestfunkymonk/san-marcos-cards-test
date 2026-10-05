import sys, itertools
sys.path.insert(0, '/home/luke/Projects/design/san-marcos-deck/build/review/courts2-KH/work/r2')
import scan as S, numpy as np
side = sys.argv[1]
bends = [float(x) for x in sys.argv[2].split(',')]
dists = [float(x) for x in sys.argv[3].split(',')]
cuffs = [float(x) for x in sys.argv[4].split(',')]
rows = []
for b, d, c in itertools.product(bends, dists, cuffs):
    W, B, m = S.metrics(side, b, d, cuff=c)
    score = min(m['cc_cuff'] / 12, m['seam_corner'] / 10, m['att_gap'] / 8, m['cc_frame'] / 10)
    rows.append((score, b, d, c, {k: round(float(v), 1) for k, v in m.items() if k != 'F'}))
rows.sort(key=lambda r: -r[0])
for r in rows[:15]:
    print(round(r[0], 2), r[1:])
