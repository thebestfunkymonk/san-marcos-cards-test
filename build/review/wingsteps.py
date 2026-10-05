from deck.motifs import lion as L
from deck import frames as F
import deck.motifs.core as C
PAL = {"leaf":"#e6b800","midrib":"#00c8ff","hatch":"#ff5050","covert":"#8f8","arm":"#fff","tip":"#f0f","terminal":"#f0f"}
def render(frag, out, vb="420 220 115 190", extra=""):
    parts=[]
    for m in frag.marks:
        col = PAL.get(m.role, "#aaa")
        if m.kind=="fill": parts.append(f'<path d="{m.d}" fill="{col}"/>')
        else: parts.append(f'<path d="{m.d}" fill="none" stroke="{col}" stroke-width="{m.w}" stroke-linecap="{m.cap}" stroke-linejoin="{m.join}"/>')
    sil = F.ace_pip_d('S')
    open(out,"w").write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}"><rect x="-1000" y="-1000" width="3000" height="3000" fill="#222"/><path d="{sil}" fill="#15242B"/>{extra}'+"".join(parts)+'</svg>')
steps=[]
orig_cut, orig_clip, orig_drop = L.cut, L.clip, L.drop_specks
def cut(f,*a,**k):
    r=orig_cut(f,*a,**k); steps.append(("cut",f,r)); return r
def clip(f,*a,**k):
    r=orig_clip(f,*a,**k); steps.append(("clip",f,r)); return r
L.cut=cut; L.clip=clip
import shapely
p = L.lion_moleca_parts()
# find in steps the ones in moleca_wing: last few
for i,(n,a,b) in enumerate(steps):
    print(i,n,len(a.marks),len(b.marks))
# render before step 6 (first feather cut) .. and each
import subprocess
for i in range(5, 14):
    n,a,b = steps[i]
    render(b, f"build/review/ws{i:02d}.svg")
    subprocess.run(["rsvg-convert","-w","300",f"build/review/ws{i:02d}.svg","-o",f"build/review/ws{i:02d}.png"])
# also feather 'fe' list: step 11 input (after cov) 
for i in range(6, 10):
    n,a,b = steps[i]
    render(a, f"build/review/wsin{i:02d}.svg")
    subprocess.run(["rsvg-convert","-w","300",f"build/review/wsin{i:02d}.svg","-o",f"build/review/wsin{i:02d}.png"])
