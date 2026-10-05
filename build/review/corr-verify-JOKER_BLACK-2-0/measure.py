import re, subprocess, sys, numpy as np
from PIL import Image
V='build/review/corr-verify-JOKER_BLACK-2-0'
def alpha(svgfile, drop=('index','stock'), extra_drop=(), z=2):
    s=open(svgfile).read()
    for k in drop+tuple(extra_drop):
        s=re.sub(r'<path[^>]*class="[^"]*%s[^"]*"[^>]*/>'%k,'',s)
    tmp=V+'/_m.svg'; open(tmp,'w').write(s)
    subprocess.run(['rsvg-convert','-z',str(z),'-o',V+'/_m.png',tmp],check=True)
    a=np.asarray(Image.open(V+'/_m.png').convert('RGBA'))[:,:,3].astype(float)/255
    return a, z
def stats(a,z,label,ylim=None):
    A=a.copy()
    if ylim: 
        A[:int(ylim[0]*z)]=0; A[int(ylim[1]*z):]=0
    ys,xs=np.nonzero(A>0.02)
    Y,X=np.mgrid[0:A.shape[0],0:A.shape[1]]
    cx=(A*X).sum()/A.sum()/z; cy=(A*Y).sum()/A.sum()/z
    print(f'{label}: bbox x {xs.min()/z:.1f}-{(xs.max()+1)/z:.1f} y {ys.min()/z:.1f}-{(ys.max()+1)/z:.1f} mid ({(xs.min()+xs.max()+1)/2/z:.1f},{(ys.min()+ys.max()+1)/2/z:.1f}) centroid ({cx:.1f},{cy:.1f})')
for f in sys.argv[1:]:
    print('==',f)
    a,z=alpha(f)
    stats(a,z,'all (no index/stock)')
    stats(a,z,'figure (y<750)',(0,750))
    a2,z=alpha(f,extra_drop=('joker-rule',))
    stats(a2,z,'figure only no wire?',(0,750))
