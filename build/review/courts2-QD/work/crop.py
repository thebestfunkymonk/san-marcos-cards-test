"""crop.py SVG OUT x0 y0 x1 y1 [scale]  — render a card-px box of an SVG at `scale`x."""
import subprocess, sys, os, hashlib
svg, out = sys.argv[1], sys.argv[2]
x0, y0, x1, y1 = map(float, sys.argv[3:7])
s = float(sys.argv[7]) if len(sys.argv) > 7 else 3.0
key = hashlib.md5((open(svg, 'rb').read()) + str(s).encode()).hexdigest()[:10]
tmp = f"/tmp/claude-1000/qdcrop_{key}.png"
os.makedirs("/tmp/claude-1000", exist_ok=True)
if not os.path.exists(tmp):
    subprocess.run(["rsvg-convert", "-w", str(int(750 * s)), svg, "-o", tmp], check=True)
w, h = int((x1 - x0) * s), int((y1 - y0) * s)
subprocess.run(["magick", tmp, "-crop", f"{w}x{h}+{int(x0*s)}+{int(y0*s)}", "+repage", out], check=True)
print(out)
