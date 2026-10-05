import glob, os, re, math, collections
import xml.etree.ElementTree as ET
from svgelements import Path as SPath
import numpy as np
NS = "{http://www.w3.org/2000/svg}"
ROOT = "/home/luke/Projects/design/san-marcos-deck"
widths = collections.Counter(); colors = collections.Counter(); tfs = collections.Counter()
orders = collections.Counter(); caps = collections.Counter()
for f in sorted(glob.glob(ROOT + "/cards/*.svg")):
    stem = os.path.basename(f)[:-4]
    root = ET.parse(f).getroot()
    assert root.get("viewBox") == "0 0 750 1050", (stem, root.get("viewBox"))
    orders[(stem if stem in ("AS","AC","AH","AD") else "*", tuple(g.get("id") for g in root if g.tag == NS+"g"))] += 1
    for g in root:
        if g.tag != NS + "g": continue
        lay = g.get("id")
        for el in g.iter():
            t = el.get("transform")
            if t: tfs[re.sub(r"[-\d.]+", "#", t)] += 1
            for k in ("fill", "stroke"):
                v = el.get(k)
                if v and v != "none": colors[(lay, k, v)] += 1
            if el.get("stroke") not in (None, "none"):
                widths[el.get("stroke-width")] += 1
                caps[(el.get("class"), el.get("stroke-linecap"), el.get("stroke-linejoin"), el.get("stroke-miterlimit"), el.get("stroke-width"))] += 1
print("layer orders:"); [print(" ", k, v) for k, v in orders.items()]
print("stroke widths:", dict(widths))
print("transforms:", dict(tfs))
print("colours by layer:"); [print(" ", k, v) for k, v in sorted(colors.items())]
print("cap/join per class:"); [print(" ", k, v) for k, v in sorted(caps.items(), key=str)]
