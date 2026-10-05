import sys, json; sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/work/jc/lab")
from facelab import *
import _jc_body as B, _jc_parts as J
V = json.loads(sys.argv[2])
def mk(v):
    def b():
        sc = K.Scene(rank="J")
        torso = K.box(240, 300, 540, 530)
        sc.add("jer", K.fill(torso, K.RED) + K.outline(torso), torso)
        bl = J.belt(torso, y=440.0, h=22.0, sag=4.0, x0=220.0, x1=560.0, front=358.0)
        sc.part("belt", bl)
        fl = B.region([(204, 434), (262, 421)], ("L", [(262, 421), (262, 453)]),
                      [(262, 453), (220, 480), (196, 482), (180, 466), (182, 446), (204, 434)])
        sc.part("forearmL", B.sleeve_part(fl, []))
        sc.part("cuffL", B.cuff((252.0, 421.0), (253.0, 453.0), 12.0))
        kind = v.pop("kind", "flat")
        if kind == "flat":
            K.flat(**v).add_to(sc, "handL", halo=0.0)
        else:
            B.belt_hand(**v).add_to(sc, "handL", halo=0.0)
        return sc
    return b
run(sys.argv[1], [mk(v) for v in V], box=(180, 400, 340, 490), width=480)
