import sys, json; sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/work/jc/lab")
from facelab import *
import _jc_paddle as PD
V = json.loads(sys.argv[2])
def mk(v):
    def b():
        sc = K.Scene(rank="J")
        sc.part("paddle", PD.paddle3(548.0, **v))
        return sc
    return b
run(sys.argv[1], [mk(v) for v in V], box=(500, 80, 600, 330), width=200)
