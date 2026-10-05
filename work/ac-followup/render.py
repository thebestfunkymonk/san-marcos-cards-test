"""Render an A♣ variant without touching cards/: 750 w, 188 w, and 3x crops.

    .venv/bin/python work/ac-followup/render.py NAME [module-path]

module-path defaults to art/AC.py. Output: work/ac-followup/out/NAME/.
"""
import importlib.util
import os
import subprocess
import sys

sys.path.insert(0, os.getcwd())
from deck import cardsvg as C
from deck import index as IX

name = sys.argv[1]
path = sys.argv[2] if len(sys.argv) > 2 else "art/AC.py"
out = os.path.join("work/ac-followup/out", name)
os.makedirs(out, exist_ok=True)
spec = importlib.util.spec_from_file_location("acvar", path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
doc = C.CardDoc("AC", stock="limestone", order=C.ACE_ORDER, title="AC variant")
doc.add_layers(C.layers_merge(mod.build()))
doc.add_layers(IX.index_fragments("A", "C"))
svg = os.path.join(out, "AC.svg")
doc.save(svg)


def rs(w, p, extra=()):
    subprocess.run(["rsvg-convert", "-w", str(w), *extra, svg, "-o", p], check=True)


rs(750, os.path.join(out, "AC_750.png"))
rs(188, os.path.join(out, "AC_188.png"))
rs(2250, os.path.join(out, "AC_2250.png"))
# 3x crops of the wreath: whole lower half, and the right branch
from PIL import Image
im = Image.open(os.path.join(out, "AC_2250.png"))
im.crop((150 * 3, 470 * 3, 600 * 3, 720 * 3)).save(os.path.join(out, "wreath_3x.png"))
im.crop((375 * 3, 480 * 3, 600 * 3, 700 * 3)).save(os.path.join(out, "wreath_right_3x.png"))
im.crop((260 * 3, 600 * 3, 490 * 3, 720 * 3)).save(os.path.join(out, "knot_3x.png"))
print(out)
