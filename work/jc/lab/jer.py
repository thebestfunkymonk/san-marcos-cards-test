"""Jerkin pattern lab: monkeypatch JC.LEAF/LEAF_L/LEAF_R and render the torso crop."""
import sys, json, importlib; sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/work/jc/lab")
from facelab import *
import JC
V = json.loads(sys.argv[2])
base = (dict(JC.LEAF), dict(JC.LEAF_L), dict(JC.LEAF_R))
def mk(v):
    def b():
        JC.LEAF = dict(base[0], **{k: tuple(x) if isinstance(x, list) else x for k, x in v.get("leaf", {}).items()})
        JC.LEAF_L = dict(base[1], **{k: tuple(x) if isinstance(x, list) else x for k, x in v.get("l", {}).items()})
        JC.LEAF_R = dict(base[2], **{k: tuple(x) if isinstance(x, list) else x for k, x in v.get("r", {}).items()})
        return JC.figure()
    return b
run(sys.argv[1], [mk(v) for v in V], box=(160, 290, 600, 515), width=660)
