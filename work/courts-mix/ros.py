import sys; sys.path.insert(0,'.')
from deck.motifs import geometric as MG
from deck.motifs import core as C
from deck import courtkit as K
from deck import tokens as T
from inkkit import geom as G
out = []
def frag_svg(f):
    s = []
    for m in f.marks:
        if m.kind == 'fill':
            s.append(f'<path d="{m.d}" fill="{T.INK}"/>')
        else:
            s.append(f'<path d="{m.d}" fill="none" stroke="{T.INK}" stroke-width="{m.w}" stroke-linecap="round" stroke-linejoin="round"/>')
    return ''.join(s)
vars_ = [
 ('crater6', MG.crater(0,0,12.4, n=6, hub=5.0, twist=48.0, dot_d=None)),
 ('crater6_norim', MG.crater(0,0,12.4, n=6, hub=5.0, twist=60.0, dot_d=None, rim=False)),
 ('crater5_dot', MG.crater(0,0,12.4, n=5, hub=0, twist=70.0, dot_d=4.2, rim=True)),
 ('rings', MG.ripple_rings(0,0,3.0, 3.6, n=3) if hasattr(MG,'ripple_rings') else C.Frag()),
 ('crater7', MG.crater(0,0,12.4, n=7, hub=6.0, twist=40.0, dot_d=None)),
]
W = 120
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W*len(vars_)*4}" height="{W*4}" viewBox="0 0 {W*len(vars_)} {W}">']
for i,(n,f) in enumerate(vars_):
    cx = W*i + W/2
    svg.append(f'<g transform="translate({cx},{W/2})"><circle r="30" fill="{T.FOIL}"/>{frag_svg(f)}</g>')
svg.append('</svg>')
open('work/courts-mix/ros.svg','w').write(''.join(svg))
