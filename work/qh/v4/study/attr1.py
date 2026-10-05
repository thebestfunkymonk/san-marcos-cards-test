import sys
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/work/qh/v4/study")
from render import render
from deck import courtkit as K
from art import _qh_face as QF, _qh_head as H, _qh_cap as CP, _qh_attr as A
import cap1

HEAD = (383.0, 204.0)


def scene(v):
    sc, cap = cap1.scene(cap1.V["o1"]) if False else (K.Scene(rank="Q"), None)
    fc = QF.queen_face(HEAD, wing_mode="hook", wing=(4.5, 62.0, 0.8), lid_sag=2.6, low_sag=6.4)
    # hose behind everything
    path = [(505, 338), (501, 300), (491, 262), (485, 228), (490, 198), (504, 178), (514, 170)]
    if v == "c":
        hp, fer = A.hose(path, w0=10, w1=12, bub=None, ferrule=9.0)
        sc.part("hose", hp, sil=False)
        sc.part("ferrule", fer, sil=False)
        sc.add("bubbles", A.bubble_rise([(522, 160), (516, 136), (508, 112), (508, 88), (516, 64)], d0=4.2,
                                        ratio=1.22, gap0=5.0, d_max=10.5), None, sil=False)
    else:
        hp, fer = A.hose(path, w0=12.5, w1=19, bub=(3.0, 8.0), gap0=5.0, gap_grow=1.1, ferrule=9.0)
        sc.part("hose", hp, sil=False)
        sc.part("ferrule", fer, sil=False)
        sc.add("bubbles", A.bubble_rise([(522, 158), (514, 130), (508, 104), (512, 76)], d0=8.4, ratio=1.12,
                                        gap0=6.0, d_max=11.0), None, sil=False)
    sc.part("hairF", H.lock([(430, 186), (440, 214), (443, 248), (442, 276), (452, 298), (466, 300)], 30.0, n=3,
                            side=-1))
    sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
    sc.part("stem", A.stem((546, 548), (546, 150), w=18.0, nodes=(0.55,)), halo=K.HALO)
    sc.part("petiole", A.petiole((548, 330), (578, 280), w=9.0, sag=-8.0), sil=False)
    sc.part("leaf", A.arrow_leaf2((578, 278), tilt=8.0, blade=76.0, half_w=23.0, lobe=(22.0, 38.0)))
    for nm, pt in A.flower3((548, 116), r_petal=38.0, petal_w=31.0, centre_r=11.0):
        sc.part("flower-" + nm, pt)
    return sc


if __name__ == "__main__":
    out = "/home/luke/Projects/design/san-marcos-deck/work/qh/v4/study/out"
    for v in sys.argv[1:]:
        log = render(scene(v), f"{out}/attr_{v}.png", box=(420, 50, 622, 360), scale=3.0, small=0.25)
        for e in log[:30]:
            print("  ", e)
