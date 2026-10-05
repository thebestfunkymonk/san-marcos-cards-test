import sys
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck"); sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/art")
import _qc_gown as GW
orig = GW.leaf_pack
def wrap(*a, **k):
    f, placed = orig(*a, **k)
    print("placed", len(placed), [(round(float(b[0])), round(float(b[1])), L, round(W,1)) for b, L, W, bd, pg in placed])
    return f, placed
GW.leaf_pack = wrap
import QC
QC.figure()
