"""qapieces.py <svg> x,y ... : QA-12 pieces near each point (as QA sees them)."""
import sys
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
from deck import qa as QA
from shapely.geometry import Point
import shapely
svg = open(sys.argv[1]).read()
pieces = QA.card_geometry(svg)
vec = QA.vector_gaps(pieces)
print("vector issues:", len(vec))
for o in vec[:20]:
    print("  ", o["gap"], o["rule"], o["at"], o["layers"])
for a in sys.argv[2:]:
    x, y = map(float, a.split(","))
    p = Point(x, y)
    print("--- near", x, y)
    for q in pieces:
        d = q["geom"].distance(p)
        if d < 4:
            b = [round(v, 1) for v in q["geom"].bounds]
            print(f"   d={d:.2f} el={q['el']} layer={q['layer']} kind={q['kind']} area={q['geom'].area:.1f} bounds={b}")
