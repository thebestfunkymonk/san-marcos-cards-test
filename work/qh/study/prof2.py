import time, sys
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
from deck import courtkit as K
from art import _qh_attr as A, _qh_body as B, _qh_face as QF, _qh_head as H
def T(name, fn):
    t=time.time(); r=fn(); print(f"{name:12s} {time.time()-t:6.2f}s"); return r
fc = T("face", lambda: QF.queen_face((383.,203.), wing_mode="hook", wing=(4.5,62.,.8), lid_sag=2.6, low_sag=6.4))
cap = T("cap", lambda: H.Cap(fc, step=16.0, length=20.0, pitch=26.0, front=(8.0, -33.0), far=(46.0, -12.0), near=(-47.0, 4.0)))
T("capbody", cap.body); T("rim", cap.rim)
for j in range(3): T(f"row{j}", lambda: cap.row(j))
T("hose", lambda: A.hose([(548, 352), (576, 300), (592, 250), (585, 200), (592, 150), (590, 112)], w=20.0))
T("bodice", lambda: B.bodice())
T("sleeveL", lambda: B.sleeve_puff(-1, (352, 314), (268, 312), (206, 352), [(196, 430), (190, 545)], [(250, 545), (268, 450), (294, 366), (330, 340)]))
T("hairL", lambda: K.hair_fall(fc, -1, K.HairSpec(top=(-44.0, -2.0), bulge=(-70.0, 60.0), bottom=(-50.0, 128.0), ribbons=5, over=10.0)))
T("leaf", lambda: A.arrow_leaf((532, 172)))
T("flower", lambda: A.flower((482, 232)))
T("clasp", lambda: K.lion_clasp((390.0, 364.0), 36.0))
