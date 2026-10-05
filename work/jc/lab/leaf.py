import sys, json; sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/work/jc/lab")
from facelab import *
import _jc_body as B
from deck.motifs import core as C
V = json.loads(sys.argv[2])
tiles = []
for i, v in enumerate(V):
    field = K.box(0, 0, 200, 200)
    f = C.Frag()
    lf = C.Frag()
    for (x, y, h) in [(60, 150, -70), (140, 150, -110), (100, 80, -70)]:
        lf += B.pecan_leaf((x, y), h, **v)
    f += K.fill(C.knockout(K.D(field), lf), K.RED)
    p = os.path.join(OUT, f"{sys.argv[1]}{i}.png")
    render([f], (0, 0, 200, 200), p, 400)
    tiles.append(p)
subprocess.run(["magick", *tiles, "+append", os.path.join(OUT, f"{sys.argv[1]}.png")], check=True)
