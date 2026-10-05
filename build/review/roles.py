import sys
from deck.motifs import *
from deck.motifs import lion as L
from deck import tokens as T
from deck import frames as F
PAL = {"leaf":"#e6b800","midrib":"#00c8ff","hatch":"#ff5050","covert":"#8f8","arm":"#fff","tip":"#f0f","terminal":"#f0f"}
def render(frag, out, vb):
    parts=[]
    for m in frag.marks:
        col = PAL.get(m.role, "#aaa")
        if m.kind=="fill":
            parts.append(f'<path d="{m.d}" fill="{col}"/>')
        else:
            parts.append(f'<path d="{m.d}" fill="none" stroke="{col}" stroke-width="{m.w}" stroke-linecap="{m.cap}" stroke-linejoin="{m.join}"/>')
    sil = F.ace_pip_d('S')
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}"><rect x="-1000" y="-1000" width="3000" height="3000" fill="#222"/><path d="{sil}" fill="#15242B"/>'+"".join(parts)+'</svg>'
    open(out,"w").write(svg)
p = L.lion_moleca_parts()
render(p["wings"], "build/review/wings-roles.svg", "420 220 115 190")
print({m.role for m in p["wings"].marks})
