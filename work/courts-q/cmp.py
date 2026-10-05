import sys, re, importlib
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
from deck import build as B
mod = B.load_art(sys.argv[1])
L = mod.build()
svg = open(sys.argv[2]).read()
for lay, frags in L.items():
    body = "".join(frags)
    print(lay, len(body), body[:80] in svg, body in svg)
