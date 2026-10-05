"""Reviewer harness: build/QA pieces with art from build/review/art_test, writing only under build/review/."""
import sys, os, importlib.util, json
ROOT = "/home/luke/Projects/design/san-marcos-deck"
sys.path.insert(0, ROOT)
REV = os.path.join(ROOT, "build", "review")
from deck import build as B, qa as Q, tokens as T
B.ROOT = os.path.join(REV, "root")
Q.QA_DIR = os.path.join(REV, "qa")
_ART = os.path.join(REV, "art_test")
def _load(pid):
    p = os.path.join(_ART, f"{pid}.py")
    if not os.path.isfile(p):
        return None
    spec = importlib.util.spec_from_file_location(f"review_art_{pid}", p)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
B.load_art = _load

def build(pid):
    a = B.build_piece(pid, "limestone"); w = B.build_piece(pid, "white")
    if a.get("error"): print(a["error"])
    return a, w

def qa(info, infow):
    r = Q.check_piece((info, infow)); r.pop("_index_region", None)
    return r

def summary(r):
    out = []
    for k, _ in Q.COLS:
        v = r.get(k)
        if isinstance(v, dict):
            out.append(f"{k}:{Q._sym(v)}" + (f"{v.get('detail')}" if v.get('ok') in (False, 'warn') else ""))
    if "error" in r: out.append("ERROR " + r["error"].splitlines()[-1])
    return "  ".join(out)

def plant(info, infow, name, mutate):
    """Write mutated copies of a built SVG (limestone + white) and QA them."""
    os.makedirs(os.path.join(REV, "plant"), exist_ok=True)
    i2, w2 = dict(info), dict(infow)
    for src, dst in ((info, i2), (infow, w2)):
        txt = mutate(open(src["svg"]).read())
        p = os.path.join(REV, "plant", f"{name}{'' if src is info else '-white'}.svg")
        open(p, "w").write(txt); dst["svg"] = p
    i2["stem"] = w2["stem"] = "PLANT-" + name
    return qa(i2, w2)

if __name__ == "__main__":
    for pid in sys.argv[1:]:
        a, w = build(pid)
        print(pid, a["status"], summary(qa(a, w)))
