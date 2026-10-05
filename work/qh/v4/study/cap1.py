import sys
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/work/qh/v4/study")
from render import render
from deck import courtkit as K
from art import _qh_face as QF, _qh_head as H, _qh_cap as CP

HEAD = (383.0, 204.0)


def scene(variant):
    sc = K.Scene(rank="Q")
    fc = QF.queen_face(HEAD, wing_mode="hook", wing=(4.5, 62.0, 0.8), lid_sag=2.6, low_sag=6.4)
    sc.part("hairN", H.lock([(322, 188), (308, 222), (304, 262), (294, 292), (276, 308), (260, 302)], 50.0, n=5,
                            side=+1, bubbles=(4.2, 5.6, 7.0), bubble_lane=2, bubble_at=0.55))
    sc.part("hairF", H.lock([(430, 186), (440, 214), (443, 248), (442, 276), (452, 298), (466, 300)], 30.0, n=3,
                            side=-1))
    sc.part("neck", K.neck(fc, bottom=299.0, width=35.0))
    sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
    cap = CP.Cap(**variant["cap"])
    sc.part("capbase", cap.base())
    if not variant.get("rim_front"):
        sc.part("rim", cap.rim())
    for k, rw in enumerate(variant.get("rows", [])):
        sc.part(f"row{k}", cap.row(**rw))
    for k, rw in enumerate(variant.get("fans", [])):
        for phi, pt in cap.petals(**rw):
            sc.part(f"fan{k}_{phi:.0f}", pt)
    if variant.get("rim_front"):
        sc.part("rim", cap.rim())
    sc.part("pearl", cap.pearl(**variant.get("pearl", {})))
    return sc, cap



CI = dict(c=(377, 194), R=62.0, yaw=24, pitch=26, tilt=6, t_front=52, t_back=112, t_side=100, rim_h=10)
CJ = dict(c=(377, 194), R=62.0, yaw=24, pitch=22, tilt=8, t_front=58, t_back=112, t_side=100, rim_h=10)
CI = dict(c=(377, 194), R=62.0, yaw=24, pitch=26, tilt=6, t_front=52, t_back=112, t_side=100, rim_h=10)
CJ = dict(c=(377, 194), R=62.0, yaw=24, pitch=22, tilt=8, t_front=58, t_back=112, t_side=100, rim_h=10)
CI = dict(c=(377, 194), R=62.0, yaw=24, pitch=26, tilt=6, t_front=52, t_back=112, t_side=100, rim_h=10)
CJ = dict(c=(377, 194), R=62.0, yaw=24, pitch=22, tilt=8, t_front=58, t_back=112, t_side=100, rim_h=10)
CK = dict(c=(377, 194), R=62.0, yaw=24, pitch=16, tilt=10, t_front=65.5, t_back=112, t_side=100, rim_h=10)
CK = dict(c=(377, 194), R=62.0, yaw=24, pitch=16, tilt=10, t_front=65.5, t_back=112, t_side=100, rim_h=10)
def fans(**kw):
    base = [dict(u0=0.62, u1=0.0, n=5, phase=0.5, widen=1.2), dict(u0=0.9, u1=0.28, n=6, phase=0.0, widen=1.15),
            dict(u0=1.02, u1=0.56, n=7, phase=0.5, widen=1.1)]
    return [dict(b, lift=0.14, tip="round", shoulder=0.5, **kw) for b in base]
V = {
    "o1": dict(cap=CK, rim_front=True, fans=fans(rib=False), pearl=dict(d=16.0, r=1.1)),
    "o2": dict(cap=CK, rim_front=True, fans=fans(rib=True, hatch_rel=0.0), pearl=dict(d=16.0, r=1.1)),
    "o3": dict(cap=CK, rim_front=True, fans=fans(rib=True, hatch_rel=45.0), pearl=dict(d=16.0, r=1.1)),
}
if __name__ == "__main__":
    import os
    out = "/home/luke/Projects/design/san-marcos-deck/work/qh/v4/study/out"
    os.makedirs(out, exist_ok=True)
    for k in sys.argv[1:] or V:
        sc, cap = scene(V[k])
        print("pole", cap.pt(0, 0), "front rim", cap.pt(cap.t_rim(0), 0), "back", cap.pt(cap.t_rim(180), 180))
        log = render(sc, f"{out}/cap_{k}.png", box=(260, 70, 510, 320), scale=3.0, small=0.25)
        for e in log[:25]:
            print("  ", e)
