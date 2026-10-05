import sys
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/work/qs/tools")
from r import render, montage
from deck import courtkit as K
from deck.motifs import core as C
import art._qs_parts as Q
V = eval(sys.argv[2])
outs = []
for i, v in enumerate(V):
    sc = K.Scene()
    bg = K.box(200, 260, 420, 520)
    sc.part("bg", K.Part(bg, K.fill(bg, K.JADE), C.Frag(), {}))
    ps = Q.laurel_sprig2(v["mouth"], v["axis"], v["stem"], leaves=v["leaves"], rac=v.get("rac"), rac_kw=v.get("rac_kw"))
    sc.part("leaves", ps["leaves"], halo=K.HALO)
    sc.part("stem", ps["stem"], halo=K.HALO)
    if "raceme" in ps:
        sc.add("raceme-halo", C.Frag(), ps["raceme"].shape, halo=K.HALO, sil=True)
        for j, fp in enumerate(ps["florets"]):
            sc.part(f"fl{j}", fp)
    sc.part("holder", ps["holder"])
    fk = v.get("fist", {})
    K.fist(fk.get("at", (324.5, 408.0)), v["axis"], shaft_w=fk.get("shaft_w", 9.0), back=fk.get("back", -1),
           wrist=fk.get("wrist", (312.0, 452.0)), wrist_w=fk.get("wrist_w", 24.0), h=fk.get("h", 30.0)).add_to(sc, "hand", halo=K.HALO)
    o = f"{sys.argv[1]}-{i}.png"
    render(sc.layers(), o, (200, 250, 400, 470), 3)
    outs.append(o)
montage(outs, sys.argv[1] + ".png", tile=f"{len(outs)}x1")
