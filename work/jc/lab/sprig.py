import sys, json; sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/work/jc/lab")
from facelab import *
import _jc_body as B
from deck.motifs import core as C
V = json.loads(sys.argv[2])
tiles = []
for i, v in enumerate(V):
    field = K.box(0, 0, 200, 200)
    lf, nf = B.sprig_field(field, **v)
    f = K.fill(C.knockout(K.D(field), lf, nf.select(lambda m: m.kind == "fill")), K.RED) + nf
    p = os.path.join(OUT, f"{sys.argv[1]}{i}.png")
    render([f], (0, 0, 200, 200), p, 400)
    tiles.append(p)
subprocess.run(["magick", *tiles, "+append", os.path.join(OUT, f"{sys.argv[1]}.png")], check=True)
