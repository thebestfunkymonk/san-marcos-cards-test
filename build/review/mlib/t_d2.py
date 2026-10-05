from rh import *
from deck.motifs import geometric as M
for R, w in ((130, T.FINE), (90, T.FINE), (40, T.MEDIUM), (40, T.FINE), (16, T.FINE)):
    d2 = M.source_rosette(375, 525, R, twist=False, w=w)
    a, b = d2.shape(), d2.mirror_x().shape()
    sd = a.symmetric_difference(b).area
    hd = a.hausdorff_distance(b)
    hatch = d2.select(lambda m: m.role == "hatch")
    ha, hb = hatch.shape(), hatch.mirror_x().shape()
    print(f"R{R} w{w} ({d2.meta['rosette']['detail']}): sym-diff vs mirror {sd:.1f}px2 (ink {a.area:.0f}); discrete hausdorff {hd:.3f}; hatch-only overlap with its mirror {ha.intersection(hb).area:.1f} of {ha.area:.1f}px2; mirror_y symdiff {a.symmetric_difference(d2.mirror_y().shape()).area:.1f}")
