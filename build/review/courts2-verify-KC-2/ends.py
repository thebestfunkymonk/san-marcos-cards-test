import numpy as np, sys
from PIL import Image
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
def thin(img):
    img=img.astype(np.uint8).copy()
    def nbrs(I):
        P=np.pad(I,1)
        p2=P[:-2,1:-1];p3=P[:-2,2:];p4=P[1:-1,2:];p5=P[2:,2:];p6=P[2:,1:-1];p7=P[2:,:-2];p8=P[1:-1,:-2];p9=P[:-2,:-2]
        return [p2,p3,p4,p5,p6,p7,p8,p9]
    changed=True
    while changed:
        changed=False
        for step in (0,1):
            n=nbrs(img); B=sum(n)
            seq=n+[n[0]]
            A=sum(((seq[i]==0)&(seq[i+1]==1)).astype(int) for i in range(8))
            p2,p3,p4,p5,p6,p7,p8,p9=n
            if step==0: c=(p2*p4*p6==0)&(p4*p6*p8==0)
            else: c=(p2*p4*p8==0)&(p2*p6*p8==0)
            m=(img==1)&(B>=2)&(B<=6)&(A==1)&c
            if m.any(): img[m]=0; changed=True
    return img.astype(bool)
def ends(fn, box):
    im=np.array(Image.open(fn).convert('RGB')).astype(int)
    x0,y0,w,h=box
    im=im[y0:y0+h, x0:x0+w]
    ink=(im.sum(-1)<200)&(abs(im[...,0]-im[...,2])<40)
    sk=thin(ink)
    k=np.ones((3,3),int); k[1,1]=0
    nb=ndi.convolve(sk.astype(int),k,mode='constant')
    ys,xs=np.nonzero(sk&(nb==1))
    return list(zip(ys,xs))
S=3
box=(417,165,1416,1380)
ea=ends('A3.png',box); eb=ends('B3.png',box)
tb=cKDTree(np.array(eb))
new=[p for p in ea if tb.query(p)[0]>6]
print('endpoints after',len(ea),'before',len(eb),'new',len(new))
merged=[]
for y,x in new:
    p=(round(139+x/S,1), round(55+y/S,1))
    if not any(abs(p[0]-q[0])<4 and abs(p[1]-q[1])<4 for q in merged): merged.append(p)
for p in sorted(merged,key=lambda p:(p[1],p[0])): print(p)
ta=cKDTree(np.array(ea))
gone=[p for p in eb if ta.query(p)[0]>6]
print('gone',len(gone))
