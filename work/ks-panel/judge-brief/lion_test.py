import sys
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
from deck.motifs import lion as L
from deck import tokens as T
f = L.lion_mark(60, 40, 40, style="solid")
lay = f.layers()
body = "".join(lay.get(k, "") if isinstance(lay.get(k,""), str) else "".join(lay[k]) for k in ("paper","jade","red","gold","ink"))
svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 80" width="120" height="80"><rect width="120" height="80" fill="{T.RED}"/>{body}</svg>'
open("/home/luke/Projects/design/san-marcos-deck/work/ks-panel/judge-brief/lion.svg","w").write(svg)
print(f.meta)
