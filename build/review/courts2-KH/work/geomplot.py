import subprocess
from shapely.geometry import Polygon, MultiPolygon, LineString
def _d(g):
    out = []
    if g.geom_type in ('Polygon',):
        for r in [g.exterior, *g.interiors]:
            xy = list(r.coords); out.append('M' + 'L'.join(f'{x:.2f},{y:.2f}' for x, y in xy) + 'Z')
    elif g.geom_type in ('LineString', 'LinearRing'):
        xy = list(g.coords); out.append('M' + 'L'.join(f'{x:.2f},{y:.2f}' for x, y in xy))
    elif hasattr(g, 'geoms'):
        for gg in g.geoms: out.append(_d(gg))
    return ''.join(out)
def plot(items, box, path, scale=10, grid=5):
    x0, y0, x1, y1 = box
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {y0} {x1-x0} {y1-y0}" width="{(x1-x0)*scale}" height="{(y1-y0)*scale}">',
         f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="white"/>']
    for gx in range(int(x0 // grid * grid), int(x1) + 1, grid):
        s.append(f'<line x1="{gx}" y1="{y0}" x2="{gx}" y2="{y1}" stroke="#ddd" stroke-width="0.1"/>')
    for gy in range(int(y0 // grid * grid), int(y1) + 1, grid):
        s.append(f'<line x1="{x0}" y1="{gy}" x2="{x1}" y2="{gy}" stroke="#ddd" stroke-width="0.1"/>')
    for g, col, fill, w in items:
        s.append(f'<path d="{_d(g)}" fill="{fill}" fill-opacity="0.3" stroke="{col}" stroke-width="{w}"/>')
    s.append('</svg>')
    open(path + '.svg', 'w').write('\n'.join(s))
    subprocess.run(['rsvg-convert', path + '.svg', '-o', path], check=True)
