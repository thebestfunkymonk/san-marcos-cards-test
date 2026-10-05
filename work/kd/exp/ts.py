import sys; sys.path.insert(0,'/home/luke/Projects/design/san-marcos-deck')
from deck.motifs import core as C
from deck import motifs as M
from deck import tokens as T
import subprocess
f = C.Frag()
f += M.tooled_scroll(20, 200, 40, height=40)
f += M.tooled_scroll(20, 120, 110, height=32)
f += M.tooled_scroll(20, 80, 170, height=30)
lay = f.layers()
svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 220 220" width="880" height="880"><rect width="220" height="220" fill="%s"/>' % T.PAPER
for L in T.LAYERS:
    if L in lay: svg += lay[L] if isinstance(lay[L], str) else "".join(lay[L])
svg += '</svg>'
open('/home/luke/Projects/design/san-marcos-deck/work/kd/exp/ts.svg','w').write(svg)
subprocess.run(['rsvg-convert','/home/luke/Projects/design/san-marcos-deck/work/kd/exp/ts.svg','-o','/home/luke/Projects/design/san-marcos-deck/work/kd/exp/ts.png'])
print(f.meta)
