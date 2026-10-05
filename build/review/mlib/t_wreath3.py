from rh import *
from deck.motifs import rice as RI
from deck.motifs import sheet_figurative as SF
from inkkit import geom as G
def stem_report(w, tag):
    stem = [p for m in w.marks if m.role=="stem" for p,_ in G.flatten(m.d)]
    tot = sum(G.Curve(p).length for p in stem)
    knot = w.select(lambda m: m.role in ("knot","knot-tail")).shape()
    rest = w.select(lambda m: m.role not in ("knot","knot-tail","terminal")).shape()
    print(f"{tag}: stem pieces {len(stem)} total stem length {tot:.1f}; knot gap to nearest mark {knot.distance(rest):.2f}")
stem_report(RI.rice_wreath_arc(375, 470, 175), "A♣ default r175")
stem_report(RI.rice_wreath_arc(0, 0, 150), "sheet r150")
stem_report(RI.rice_wreath_arc(0, 0, 150, leaf_len=64, ratio=10.0), "test r150 64/10")
stem_report(RI.rice_wreath_arc(0, 0, 175, angle=40), "r175 angle 40")
t = SF.tuck_lens_demo()
stem_report(t.select(lambda m: True), "tuck demo (andante+wreath)")
