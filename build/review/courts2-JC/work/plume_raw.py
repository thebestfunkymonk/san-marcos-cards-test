import sys, subprocess; sys.path.insert(0,'.'); sys.path.insert(0,'art')
from deck import courtkit as K
import JC, _jc_head as H
lines = eval(sys.argv[1]); out = sys.argv[2]
kw = dict(JC.PLUME_KW); kw['lines'] = lines
vane, quill = H.heron_plume3(JC.PLUME, **kw)
f = vane.frag
svg = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="440 60 100 70" width="1000" height="700"><rect x="0" y="0" width="1000" height="1000" fill="#F4EFE3"/>']
for m in f.marks:
    if m.kind == 'fill':
        svg.append(f'<path d="{m.d}" fill="{"#c33" if m.role=="terminal" else m.color}"/>')
    else:
        col = {'current': '#06c', 'outline': '#162329'}.get(m.role, '#162329')
        svg.append(f'<path d="{m.d}" fill="none" stroke="{col}" stroke-width="{m.w}" stroke-linecap="round" stroke-linejoin="round"/>')
svg.append('</svg>')
open(out + '.svg', 'w').write('\n'.join(svg))
subprocess.run(['rsvg-convert', out + '.svg', '-o', out + '.png'])
