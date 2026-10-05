import sys, numpy as np
sys.path.insert(0, '/home/luke/Projects/design/san-marcos-deck')
from deck import qa as Q, tokens as T, frames as F
from inkkit import geom as G
def balance(svg_path, S=2):
    svg = open(svg_path).read()
    W3, H3 = T.W * S, T.H * S
    alpha = {}
    for L in T.LAYERS:
        if f'<g id="{L}" clip-path="url(#card)"></g>' in svg:
            alpha[L] = np.zeros((H3, W3), np.uint8); continue
        alpha[L] = Q._rsvg(Q._isolate(svg, L), W3)[..., 3]
    vis = {}; cover = np.zeros((H3, W3), np.float32)
    for L in reversed(list(T.LAYERS)):
        if L == 'paper': continue
        a = alpha[L].astype(np.float32) / 255.0
        vis[L] = a * (1 - cover); cover += vis[L]
    halves = G.difference(F.art_window_d(), G.rect_d(0, F.BAND_Y0, T.W, F.BAND_Y1 - F.BAND_Y0))
    win = Q._poly_mask(halves, (H3, W3), S)
    n = win.sum()
    bal = {L: round(float(vis[L][win].sum() / n * 100), 2) for L in vis}
    bal['paper'] = round(100 - sum(bal.values()), 2)
    return bal
if __name__ == '__main__':
    for p in sys.argv[1:]:
        print(p.split('/')[-2], balance(p))
