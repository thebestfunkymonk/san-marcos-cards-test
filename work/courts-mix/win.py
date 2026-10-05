import sys, json; sys.path.insert(0,'.')
from art import _kh_window as KW
from deck import courtkit as K, tokens as T
from deck.motifs import core as C
from inkkit import geom as G
COL = {'jade': T.JADE, 'red': T.RED, 'gold': T.FOIL, 'ink': T.INK}
ORDER = ['jade','red','gold','ink']
def svg_of(frag):
    by = {L: [] for L in ORDER}
    for m in frag.marks:
        c = COL.get(m.layer, T.INK)
        if m.kind == 'fill':
            by[m.layer].append(f'<path d="{m.d}" fill="{c}" fill-rule="evenodd"/>')
        else:
            by[m.layer].append(f'<path d="{m.d}" fill="none" stroke="{c}" stroke-width="{m.w}" stroke-linecap="{m.cap or "round"}" stroke-linejoin="round"/>')
    return ''.join(''.join(by[L]) for L in ORDER)
variants = json.loads(sys.argv[1])
cells = []
for i, kw in enumerate(variants):
    cx, cy = 375.0, 432.0
    p = KW.window(cx, cy, **kw)
    sc = K.Scene()
    sc.add('bg', K.fill(K.box(290, 360, 460, 500), K.JADE), K.box(290,360,460,500), sil=False)
    sc.part('win', p)
    f = sc.compose(contour=None)
    cells.append(f'<g transform="translate({i*180-290},-360)">{svg_of(f)}</g>')
W = 180*len(variants)
open('work/courts-mix/win.svg','w').write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W*4}" height="{150*4}" viewBox="0 0 {W} 150"><rect width="{W}" height="150" fill="{T.PAPER}"/>' + ''.join(cells) + '</svg>')
print('log', len(sc.heal_log))
for e in sc.heal_log: print(e)
