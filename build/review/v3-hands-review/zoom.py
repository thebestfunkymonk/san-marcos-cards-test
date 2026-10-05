import sys, os, warnings
ROOT = "/home/luke/Projects/design/san-marcos-deck"
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, "tools"))
import hand_specimen as HS
from deck import courtkit as K
OUT = os.path.join(ROOT, "build/review/v3-hands-review/zoom"); os.makedirs(OUT, exist_ok=True)
rows = HS.rows()
for spec in sys.argv[1:]:
    ri, ci, scale = spec.split(":"); ri, ci, scale = int(ri), int(ci), float(scale)
    c = rows[ri][1][ci]
    sc, ctr = HS._scene(c)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore"); hand = getattr(K, c["fn"])(*c["args"], **c["kw"])
    b = hand.hand.shape.bounds
    pad = 4; size = max(b[2]-b[0], b[3]-b[1]) + 2*pad
    ctr = ((b[0]+b[2])/2, (b[1]+b[3])/2)
    svg = HS._svg(sc, ctr, size)
    HS._render(svg, os.path.join(OUT, f"{ri:02d}_{ci:02d}_x{int(scale)}.png"), size*scale)
