"""gaps.py SVG... : uncapped QA-12 raster ink thin / narrow-gap clusters (top half only, y < 511)."""
import sys
sys.path.insert(0, ".")
from deck import qa as QA, tokens as T
S = QA.SCALE
for svg in sys.argv[1:]:
    txt = open(svg).read()
    a = QA._rsvg(QA._isolate(txt, "ink"), T.W * S)[..., 3]
    thin, gaps = QA._morph(a > 127)
    g = QA._clusters(gaps, QA.GAP_CLUSTER * S * S, S, limit=999)
    t = QA._clusters(thin, QA.LINE_CLUSTER * S * S, S, limit=999)
    top = [c for c in g if c["bbox"][1] < 511]
    print(svg.split("/")[-2], "gaps", len(g), "thin", len(t))
    for c in sorted(top, key=lambda c: (c["bbox"][1], c["bbox"][0])):
        print("   ", c["bbox"], c["area"])
