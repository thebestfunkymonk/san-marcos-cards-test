import sys, subprocess
sys.path.insert(0,'/home/luke/Projects/design/san-marcos-deck')
from deck import courtkit as K, tokens as T
from deck.motifs import geometric as MG, core as C
f = C.Frag()
bg = K.box(0, 0, 400, 80)
f += K.fill(bg, K.JADE)
variants = [dict(span=18, jamb=9, key=(4.5, 26), ring=None), dict(span=14, jamb=14, key=(3.0, 24), ring=6.3),
            dict(span=16, jamb=12, key=(3.5, 22), ring=6.3), dict(span=14, jamb=16, key=(5.0, 30), ring=None),
            dict(span=18, jamb=12, key=(4.0, 20), ring=6.3)]
x = 30
for v in variants:
    for k in range(2):
        f += MG.arch(x + k * (v['span'] + (2*(v['ring'] or 0)) + 10), 70, v['span'], v['jamb'], key=v['key'], ring=v['ring'], w=K.FINE)
    x += 2 * (v['span'] + 2*(v['ring'] or 0) + 10) + 14
f += K.line(C.polyline_d([(0,70),(400,70)]), K.FINE, style="rule")
lay = f.layers()
parts = [lay[L] for L in T.LAYERS if lay.get(L)]
svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 80" width="1200" height="240"><rect width="400" height="80" fill="{T.PAPER}"/>' + "".join(parts) + "</svg>"
open('/home/luke/Projects/design/san-marcos-deck/work/qd/out/parts/arch.svg','w').write(svg)
subprocess.run(["rsvg-convert","-w","1200","/home/luke/Projects/design/san-marcos-deck/work/qd/out/parts/arch.svg","-o","/home/luke/Projects/design/san-marcos-deck/work/qd/out/parts/arch.png"],check=True)
