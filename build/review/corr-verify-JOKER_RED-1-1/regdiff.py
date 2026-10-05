import sys; sys.path.insert(0,'/home/luke/Projects/design/san-marcos-deck/build/review/corr-verify-JOKER_RED-1-1')
from measure import *
S=2
old=render(strip('build/gallery/svg/JOKER-RED.svg'),750*S)
new=render(strip('cards/JOKER-RED.svg'),750*S)
old[ (690-8)*S:]=0  # drop old caption
new[(762-8)*S:]=0
dx,dy=15*S,64*S
sh=np.zeros_like(old)
sh[dy:, dx:]=old[:old.shape[0]-dy, :old.shape[1]-dx]
# composite on white to compare colors
def comp(a):
    return a[...,:3]*a[...,3:4]+ (1-a[...,3:4])
A=comp(sh); B=comp(new)
d=np.abs(A-B).sum(-1)
mask=d>0.3
ys,xs=np.nonzero(mask)
print('diff pixels', mask.sum())
# cluster by coarse grid
from scipy import ndimage
lab,n=ndimage.label(ndimage.binary_dilation(mask,iterations=6))
for i,sl in enumerate(ndimage.find_objects(lab)):
    cnt=(mask[sl]).sum()
    if cnt<5: continue
    print(f' region x {sl[1].start/S:.0f}-{sl[1].stop/S:.0f} y {sl[0].start/S:.0f}-{sl[0].stop/S:.0f} px {cnt}')
img=np.ones(B.shape)
img[...]=B*0.35+0.65
img[mask]=[1,0,1]
Image.fromarray((img*255).astype(np.uint8)).save(OUT+'regdiff.png')
