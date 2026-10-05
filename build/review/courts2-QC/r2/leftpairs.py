import sys, itertools
sys.argv = [sys.argv[0], "/dev/null", "min_w=12.6", "sliver=(4.2,25.0)", "HIDE=1", "lengths=(145.,125.,110.,100.)", "max_n=0"]
src = open("build/review/courts2-QC/r2/packx.py").read().split("t = time.time()")[0]
exec(src)
import numpy as np
from shapely.geometry import Point
from shapely.prepared import prep
import _qc_gown as GW
# feasibility = leaf_pack with a single candidate: restrict via monkeypatched grid (cheap: brute force with max_n=1 on shifted origins)
feas = []
soft_r = K.R(soft)
for L in (145., 125., 110., 100.):
    for ox in np.arange(0, 6.0, 2.0):
        for oy in np.arange(0, 6.0, 2.0):
            pk = dict(pack); pk.update(lengths=(L,), max_n=40, origin=(375.0 + ox, 330.0 + oy), grid=6.0)
            lf, placed = GW.leaf_pack(allowed.intersection(K.box(0, 0, 352, 700)), soft=soft, tip_zone=tz, **pk)
            for b, L_, W, bd, pg in placed:
                feas.append((tuple(np.round(b, 1)), L_, pg))
print(len(feas), "placements seen")
