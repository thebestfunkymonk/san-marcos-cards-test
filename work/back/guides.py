"""Guide overlay: polar grid, limit region, clearance zones, on top of a quick render."""
import sys, subprocess
sys.path.insert(0, '.')
import numpy as np
from inkkit import geom as G
from art import _back_geo as BG

def guides_svg():
    out = []
    lim = BG.limit_region()
    ext = np.asarray(lim.exterior.coords)
    out.append('<path d="M' + 'L'.join(f'{x:.1f} {y:.1f}' for x, y in ext) + 'Z" fill="none" stroke="#ff9" stroke-width="0.8" stroke-dasharray="4 3"/>')
    for r in range(150, 425, 25):
        out.append(f'<circle cx="375" cy="525" r="{r}" fill="none" stroke="#f80" stroke-width="{0.8 if r % 50 else 1.2}" opacity="0.6"/>')
    for c in range(0, 360, 15):
        x0, y0 = BG.pol(140, c); x1, y1 = BG.pol(430, c)
        out.append(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="#f0f" stroke-width="{1.2 if c % 30 == 0 else 0.5}" opacity="0.6"/>')
    return "".join(out)

if __name__ == '__main__':
    src, dst = sys.argv[1], sys.argv[2]
    s = open(src).read()
    s = s.replace('</svg>', guides_svg() + '</svg>')
    open('/tmp/claude-1000/g.svg', 'w').write(s)
    subprocess.run(['rsvg-convert', '-w', sys.argv[3] if len(sys.argv) > 3 else '750', '/tmp/claude-1000/g.svg', '-o', dst], check=True)
