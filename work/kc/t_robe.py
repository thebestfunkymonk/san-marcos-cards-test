import sys, subprocess, importlib.util
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck"); sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/work/kc")
from snap import render
spec = importlib.util.spec_from_file_location("kc", "/home/luke/Projects/design/san-marcos-deck/art/KC.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
variants = eval(sys.argv[1])
outs = []
for i, v in enumerate(variants):
    sc = m.figure(v)
    o = f"/home/luke/Projects/design/san-marcos-deck/work/kc/t/robe{i}.png"
    render(sc.layers(), o, (139, 250, 472, 261), 1.5)
    outs.append(o)
subprocess.run(["magick", *outs, "-append", "/home/luke/Projects/design/san-marcos-deck/work/kc/t/robes.png"], check=True)
