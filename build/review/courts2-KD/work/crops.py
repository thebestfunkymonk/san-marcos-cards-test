"""crops.py <svg> <outdir> <scale> name:x0,y0,x1,y1 ...  (card px) -> <outdir>/<name>_<scale>x.png"""
import os, subprocess, sys, tempfile
svg, out, s = sys.argv[1], sys.argv[2], float(sys.argv[3])
os.makedirs(out, exist_ok=True)
full = os.path.join(out, f"_full_{s:g}x.png")
if not os.path.exists(full) or os.path.getmtime(full) < os.path.getmtime(svg):
    subprocess.run(["rsvg-convert", "-w", str(int(750 * s)), svg, "-o", full], check=True)
for spec in sys.argv[4:]:
    name, box = spec.split(":")
    x0, y0, x1, y1 = map(float, box.split(","))
    W, H = int((x1 - x0) * s), int((y1 - y0) * s)
    X, Y = int(x0 * s), int(y0 * s)
    subprocess.run(["magick", full, "-crop", f"{W}x{H}+{X}+{Y}", "+repage", os.path.join(out, f"{name}_{s:g}x.png")], check=True)
