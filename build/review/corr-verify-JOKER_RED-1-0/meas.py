import numpy as np, sys
from PIL import Image
for name in sys.argv[1:]:
    a = np.asarray(Image.open(name).convert('RGBA')).astype(float)
    al = a[...,3]/255
    ys, xs = np.nonzero(al > 0.1)
    print(name, 'bbox all x', xs.min(), xs.max()+1, 'y', ys.min(), ys.max()+1)
    fig = al.copy(); fig[740:] = 0
    ys, xs = np.nonzero(fig > 0.1)
    print('  fig bbox x %d-%d y %d-%d' % (xs.min(), xs.max()+1, ys.min(), ys.max()+1), 'mid x', (xs.min()+xs.max()+1)/2, 'mid y', (ys.min()+ys.max()+1)/2)
    Y, X = np.mgrid[0:al.shape[0], 0:al.shape[1]]
    w = fig
    print('  fig alpha centroid (%.1f, %.1f)' % ((X*w).sum()/w.sum(), (Y*w).sum()/w.sum()))
    # darkness weighted: luminance of rgb on paper
    rgb = a[...,:3]/255
    lum = 0.2126*rgb[...,0]+0.7152*rgb[...,1]+0.0722*rgb[...,2]
    paper = np.array([0xF4,0xEF,0xE3])/255
    pl = 0.2126*paper[0]+0.7152*paper[1]+0.0722*paper[2]
    dk = np.clip(pl - lum, 0, None) * w
    print('  darkness centroid (%.1f, %.1f)' % ((X*dk).sum()/dk.sum(), (Y*dk).sum()/dk.sum()))
    cap = al.copy(); cap[:740] = 0
    ys, xs = np.nonzero(cap > 0.1)
    if len(ys): print('  caption bbox x %d-%d y %d-%d' % (xs.min(), xs.max()+1, ys.min(), ys.max()+1))
    ys, xs = np.nonzero(al > 0.1)
    print('  block mid y', (ys.min()+ys.max()+1)/2)
