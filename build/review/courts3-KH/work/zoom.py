"""zoom.py name x y w h scale [svg ...] -> crops (before|after side by side if 2 svgs), with grid ticks every 5 card px."""
import sys, subprocess, os, re
name, x, y, w, h, s = sys.argv[1], *map(float, sys.argv[2:7])
svgs = sys.argv[7:] or [os.path.join(os.path.dirname(os.path.abspath(__file__)), "prev_KH.svg"),
                        "/home/luke/Projects/design/san-marcos-deck/cards/KH.svg"]
out = os.path.dirname(os.path.abspath(__file__))
pngs = []
for i, f in enumerate(svgs):
    t = open(f).read()
    t = re.sub(r'<svg[^>]*>', f'<svg xmlns="http://www.w3.org/2000/svg" width="{w*s:.0f}" height="{h*s:.0f}" viewBox="{x} {y} {w} {h}">', t, count=1)
    # grid: every 5 px faint magenta, every 10 labelled via tick
    g = []
    import math
    for gx in range(int(math.ceil(x/5))*5, int(x+w)+1, 5):
        g.append(f'<line x1="{gx}" y1="{y}" x2="{gx}" y2="{y+h}" stroke="#ff00ff" stroke-opacity="{0.35 if gx%10==0 else 0.12}" stroke-width="{1.0/s}"/>')
    for gy in range(int(math.ceil(y/5))*5, int(y+h)+1, 5):
        g.append(f'<line x1="{x}" y1="{gy}" x2="{x+w}" y2="{gy}" stroke="#ff00ff" stroke-opacity="{0.35 if gy%10==0 else 0.12}" stroke-width="{1.0/s}"/>')
    if s >= 6:
        t = t.replace('</svg>', ''.join(g) + '</svg>')
    tmp = f"{out}/_z{i}.svg"; open(tmp, "w").write(t)
    p = f"{out}/{name}_{i}.png"
    subprocess.run(["rsvg-convert", tmp, "-o", p], check=True)
    pngs.append(p)
dst = f"{out}/{name}_{int(s)}x.png"
if len(pngs) > 1:
    subprocess.run(["magick", pngs[0], "-bordercolor", "magenta", "-border", "3", pngs[1], "-bordercolor", "magenta", "-border", "3", "+append", dst], check=True)
else:
    os.replace(pngs[0], dst)
print(dst, f"(x0={x}, y0={y}, grid 5px; labels: left=before right=after)")
