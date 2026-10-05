import sys, itertools
sys.path.insert(0, '/home/luke/Projects/design/san-marcos-deck/build/review/courts2-KH/work/r2')
import scan as S, numpy as np
side = sys.argv[1]
L = lambda i: [float(x) for x in sys.argv[i].split(',')]
bends, dists, cuffs, widths, wws = L(2), L(3), L(4), L(5), L(6)
thr = dict(cc=10.0, seam=6.5, att=7.0)
rows = []
for b, d, c, w, ww in itertools.product(bends, dists, cuffs, widths, wws):
    W, B, m = S.metrics(side, b, d, cuff=c, width=w, wrist_w=ww)
    score = min(m['cc_cuff'] / thr['cc'], m['seam_corner'] / thr['seam'], m['att_gap'] / thr['att'], m['cc_frame'] / 10)
    rows.append((round(score, 2), b, d, c, w, ww, {k: round(float(v), 1) for k, v in m.items() if k not in ('F', 'contour_on_cuff')}))
rows.sort(key=lambda r: -r[0])
for r in rows[:int(sys.argv[7]) if len(sys.argv) > 7 else 20]:
    print(r)
