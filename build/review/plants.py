import sys, os, re, math
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/build/review")
from harness import *
from inkkit import geom as G
from deck import frames as F, pips as P
import shapely

info, infow = build("KS")
def into(layer, frag):
    return lambda t: t.replace(f'<g id="{layer}" clip-path="url(#card)">', f'<g id="{layer}" clip-path="url(#card)">' + frag, 1)
def at_end(layer, frag):
    def f(t):
        i = t.index(f'<g id="{layer}"'); j = t.index("</g>\n", t.index("\n", i)) if False else None
        # insert right before this layer's closing tag (layer groups are flat siblings)
        k = t.index('<g id="', i + 5) if layer != "ink" else t.index("</svg>")
        close = t.rindex("</g>", i, k)
        return t[:close] + frag + t[close:]
    return f
tests = {}
# P1: <symbol>/<use> (brief §E.1 literally suggests <symbol>): illegal 2.5 stroke inside the symbol
tests["P1-symbol-use"] = at_end("ink", '<defs><symbol id="s1"><path d="M300 200l100 0" stroke="#15242B" stroke-width="2.5" fill="none"/></symbol></defs><use href="#s1" fill="none"/>')
# P2: nested <svg> whose viewBox scales a FINE stroke x3 (renders 6.3 px)
tests["P2-nested-svg-scale"] = at_end("ink", '<svg x="300" y="150" width="300" height="300" viewBox="0 0 100 100"><path d="M0 10l100 0" stroke="#15242B" stroke-width="2.1" fill="none"/></svg>')
# P3: CSS transform property in a style attribute
tests["P3-css-transform"] = at_end("ink", '<path d="M150 250l50 0" stroke="#15242B" stroke-width="2.1" fill="none" style="transform:scale(2)"/>')
# P4: two parallel FINE strokes 5.5 apart centre-to-centre = 3.4 px paper gap (< 4.2, §I.12)
tests["P4-parallel-3.4gap"] = at_end("ink", '<path d="M300 240l150 0M300 245.5l150 0M300 805l150 0M300 810.5l150 0" stroke="#15242B" stroke-width="2.1" fill="none"/>')
# P5: thin FINE gold lines on a red field (§C.4 / §I.5)
tests["P5-gold-on-red"] = lambda t: at_end("gold", '<path d="M330 310l0 30M345 310l0 30M405 710l0 30M420 710l0 30" stroke="#B08D57" stroke-width="2.1" fill="none"/>')(t)
# P6: 1.3 px wide FILLED hairline (outlined stroke, below HAIRLINE 1.6) in gold
thin = G.outline(G.poly_d([(420, 200), (560, 200)]), 1.3, cap="butt", join="miter")
thin2 = G.rotate180(thin, 375, 525)
tests["P6-fill-1.3px"] = at_end("gold", f'<path d="{thin}{thin2}" fill="#B08D57"/>')
# P7: 2.0 px knockout line inside the red collar (brief min 2.5, §I.12)
tests["P7-ko-2.0px"] = None  # built below as an art module variant
# P8: opacity & a paper cover & named colour (sanity: should be caught)
tests["P8-paper-cover"] = at_end("ink", '<path d="M200 400h40v40h-40z" fill="#f4efe3"/><path d="M510 610h40v40h-40z" fill="#f4efe3"/>')
for name, mut in tests.items():
    if mut is None: continue
    r = plant(info, infow, name, mut)
    print(f"{name:22}", summary(r))
