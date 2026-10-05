import re, subprocess, io, sys
import numpy as np
from PIL import Image
OUT='/home/luke/Projects/design/san-marcos-deck/build/review/corr-verify-JOKER_RED-1-1/'
def strip(svg):
    s=open(svg).read()
    s=re.sub(r'<path[^>]*class="[^"]*(index|stock)[^"]*"[^>]*/>','',s)
    return s
def render(s, w=750):
    p=subprocess.run(['rsvg-convert','-w',str(w),'-f','png'],input=s.encode(),capture_output=True,check=True)
    return np.asarray(Image.open(io.BytesIO(p.stdout)).convert('RGBA')).astype(float)/255
def stats(a, name, cap_y=740):
    al=a[...,3]
    H,W=al.shape
    ys,xs=np.nonzero(al>0.1)
    print(f'{name}: all bbox x {xs.min()}-{xs.max()+1} y {ys.min()}-{ys.max()+1} mid ({(xs.min()+xs.max()+1)/2:.1f},{(ys.min()+ys.max()+1)/2:.1f})')
    fig=al.copy(); fig[cap_y:]=0
    ys,xs=np.nonzero(fig>0.1)
    Y,X=np.mgrid[0:H,0:W]+0.5
    cx=(fig*X).sum()/fig.sum(); cy=(fig*Y).sum()/fig.sum()
    # darkness-weighted
    lum=0.2126*a[...,0]+0.7152*a[...,1]+0.0722*a[...,2]
    dk=fig*(1-lum)
    dx=(dk*X).sum()/dk.sum(); dy=(dk*Y).sum()/dk.sum()
    print(f'  figure bbox x {xs.min()}-{xs.max()+1} y {ys.min()}-{ys.max()+1}; bbox mid x {(xs.min()+xs.max()+1)/2:.1f}; alpha centroid ({cx:.1f},{cy:.1f}); dark centroid ({dx:.1f},{dy:.1f}); ink area {fig.sum():.0f}')
    cap=al.copy(); cap[:cap_y]=0
    ys2,xs2=np.nonzero(cap>0.1)
    print(f'  caption bbox x {xs2.min()}-{xs2.max()+1} y {ys2.min()}-{ys2.max()+1}')
    print(f'  gap lowest fig ink -> caption top ink {ys2.min()-(ys.max()+1)}; -> rule centre 762: {762-(ys.max()+1)}')
    # left/right mass moments about 375
    m=(fig*(X-375)).sum()/fig.sum()
    # quadrant masses
    L=fig[:, :375].sum(); R=fig[:,375:].sum()
    print(f'  mass L {L:.0f} R {R:.0f} ratio {L/R:.3f}')
    # lowest ink where
    row=ys.max()
    print('  lowest ink row x range', np.nonzero(fig[row]>0.1)[0].min(), np.nonzero(fig[row]>0.1)[0].max())
    # index zone clearance: x<130,y<310 and 180 copy
    zone=fig[:310,:130]
    print('  ink in index zone', (zone>0.1).sum())
    return fig
if __name__=='__main__':
    for svg,name in [(a,a) for a in sys.argv[1:]]:
        a=render(strip(svg)); stats(a,name)
