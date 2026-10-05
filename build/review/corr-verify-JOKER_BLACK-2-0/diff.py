import re, subprocess, numpy as np
from PIL import Image
V='build/review/corr-verify-JOKER_BLACK-2-0'
def strip_idx(s):
    s=re.sub(r'<path[^>]*class="[^"]*(index|stock|joker-rule)[^"]*"[^>]*/>','',s)
    return s
def render(s, out, z=3):
    open(out+'.svg','w').write(s)
    subprocess.run(['rsvg-convert','-z',str(z),'-b','white','-o',out,out+'.svg'],check=True)
    return np.asarray(Image.open(out).convert('RGB')).astype(int)
orig=open('build/gallery/svg/JOKER-BLACK.svg').read()
new=open('cards/JOKER-BLACK.svg').read()
o=strip_idx(orig); n=strip_idx(new)
# shift original groups
o2=re.sub(r'(<svg[^>]*>)', r'\1<g transform="translate(-8.4,72.8)">', o, count=1).replace('</svg>','</g></svg>')
# clip-path on groups uses userSpaceOnUse so shifting moves clip too; fine
A=render(o2, V+'/o_shift.png'); B=render(n, V+'/n.png')
d=(np.abs(A-B).sum(2)>60)
ys,xs=np.nonzero(d)
print('diff px', d.sum())
Image.fromarray((~d*255).astype(np.uint8)).save(V+'/diffmask.png')
# cluster by region
from scipy import ndimage
lab,nl=ndimage.label(ndimage.binary_dilation(d,iterations=6))
for i,sl in enumerate(ndimage.find_objects(lab)):
    cnt=d[sl].sum()
    if cnt<5: continue
    print(i, 'x %.1f-%.1f y %.1f-%.1f'%(sl[1].start/3,sl[1].stop/3,sl[0].start/3,sl[0].stop/3), cnt)
