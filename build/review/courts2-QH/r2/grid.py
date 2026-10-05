"""grid.py in.svg x y w h scale out.png [step] — crop a card SVG to a viewBox, overlay a labelled card-px grid."""
import re, subprocess, sys, tempfile, os
src, x, y, w, h, s, out = sys.argv[1:8]
step = float(sys.argv[8]) if len(sys.argv) > 8 else 5.0
x, y, w, h, s = map(float, (x, y, w, h, s))
svg = open(src).read()
svg = re.sub(r'<svg [^>]*>', f'<svg xmlns="http://www.w3.org/2000/svg" width="{w*s:.0f}" height="{h*s:.0f}" viewBox="{x} {y} {w} {h}">', svg, count=1)
g = ['<g stroke="#ff00ff" stroke-width="%.3f" opacity="0.55">' % (0.6 / s * 2)]
import math
gx = math.ceil(x / step) * step
while gx <= x + w:
    sw = 1.2 / s * 2 if gx % (step * 2) == 0 else 0.5 / s * 2
    g.append(f'<line x1="{gx}" y1="{y}" x2="{gx}" y2="{y+h}" stroke-width="{sw:.3f}"/>')
    if gx % (step * 2) == 0:
        g.append(f'<text x="{gx+0.3}" y="{y+10/s*2:.2f}" font-size="{9/s*2:.2f}" fill="#ff00ff" stroke="none">{gx:g}</text>')
    gx += step
gy = math.ceil(y / step) * step
while gy <= y + h:
    sw = 1.2 / s * 2 if gy % (step * 2) == 0 else 0.5 / s * 2
    g.append(f'<line x1="{x}" y1="{gy}" x2="{x+w}" y2="{gy}" stroke-width="{sw:.3f}"/>')
    if gy % (step * 2) == 0:
        g.append(f'<text x="{x+0.3}" y="{gy-0.3}" font-size="{9/s*2:.2f}" fill="#ff00ff" stroke="none">{gy:g}</text>')
    gy += step
g.append('</g>')
svg = svg.replace('</svg>', '\n'.join(g) + '</svg>')
fd, tmp = tempfile.mkstemp(suffix='.svg'); os.close(fd)
open(tmp, 'w').write(svg)
subprocess.run(['rsvg-convert', '-w', str(int(w * s)), tmp, '-o', out], check=True)
os.remove(tmp)
