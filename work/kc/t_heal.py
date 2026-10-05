import sys
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck"); sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/work/kc")
from deck import courtkit as K
import art._kc_crown as CR, art._kc_beard as KB
kw = eval(sys.argv[1])
fc = K.face((375.0, 207.0), "frontal", age="elder", lids="heavy", lid_sag=3.6, pupil_tuck=-1.6, brow_drop=4.0, brow_sag=3.4, brow_out=37.0, nose_bot_dy=23.0)
hs = K.HairSpec(top=(-52.0, -30.0), bulge=(-64.0, 40.0), bottom=(-53.0, 110.0), ribbons=4)
sc = K.Scene(rank="K")
for s in (-1, 1): sc.part(f"hair{s}", K.hair_fall(fc, s, hs))
sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
mo = K.moustache(fc, K.MoustacheSpec(root=(-1.5, 8.5), tip=(-32.0, 30.0), arch=7.0))
sc.part("beard", KB.spray_beard(fc, mo, **kw))
sc.part("moustache", mo)
sc.compose()
import collections; print(collections.Counter((e["role"], e["action"]) for e in sc.heal_log))
