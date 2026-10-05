"""dev render of art.QS: dev.py OUT_PREFIX [--log] [--crop x0,y0,x1,y1,scale ...]
Writes OUT_PREFIX.png (top half at 1.5x, framed like the card window) and any crops."""
import sys, time
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/work/qs/tools")
from r import render
from deck import frames as F, tokens as T
from deck.motifs import core as C
out = sys.argv[1]
t = time.time()
import art.QS as QS
sc = QS.figure()
res = sc.compose()
lay = {k: [v] for k, v in res.layers().items()}
# add the frame + pip for context
from inkkit import svg as S
pip = S.path(F.corner_pip_d("S"), fill=T.INK)
lay.setdefault("ink", []).append(pip)
lay["ink"].append(S.path(F.art_window_d(), fill="none", stroke="#999999", stroke_width=0.8))
un = [e for e in sc.heal_log if e.get("action") == "UNRESOLVED"]
print(f"compose {time.time()-t:.1f}s heal {len(sc.heal_log)} unresolved {len(un)}")
render(lay, out + ".png", (130, 45, 620, 525), 1.5)
for a in sys.argv[2:]:
    if a.startswith("--crop"):
        continue
for i, a in enumerate(sys.argv):
    if a == "--crop":
        x0, y0, x1, y1, s = [float(v) for v in sys.argv[i + 1].split(",")]
        render(lay, f"{out}-c{i}.png", (x0, y0, x1, y1), s)
if "--log" in sys.argv:
    from collections import Counter
    cnt = Counter((e.get("action"), e.get("role"), e.get("layer"), str(e.get("near"))) for e in sc.heal_log)
    for k, v in cnt.most_common(40):
        print(v, k)
    for e in un:
        print("UNRESOLVED", e)
