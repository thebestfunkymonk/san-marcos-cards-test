import sys, subprocess
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/work/jb/src")
import shapely
from inkkit import geom as G
import _joker_black_pose as P
import _joker_black_props as PR
sil = shapely.union_all([G.to_shape(P.body_d()), G.to_shape(P.bill_d())])
cells = []
variants = [(34, (-22, -6)), (60, (-22, -6)), (80, (-22, -6)), (100, (-22, -6)), (-30, (22, -6)), (160, (0, -30))]
for i, (sw, piv) in enumerate(variants):
    PR.COR_SWING = sw
    PR.COR_PIVOT = piv
    cor = PR.coronet().difference(sil.buffer(4.2))
    ox = (i % 3) * 200 - (P.BILL_TIP[0] - 100)
    oy = (i // 3) * 200 - (P.BILL_TIP[1] - 60)
    cells.append(f'<g transform="translate({ox},{oy})"><path d="{G.from_shape(sil)}" fill="#15242B"/><path d="{G.from_shape(cor)}" fill="#B08D57"/></g>')
    cells.append(f'<text x="{(i%3)*200+5}" y="{(i//3)*200+15}" font-size="12">{sw} {piv}</text>')
svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400" width="1800" height="1200"><rect width="600" height="400" fill="#F4EFE3"/>{"".join(cells)}</svg>'
open("/home/luke/Projects/design/san-marcos-deck/work/jb/draft/cor.svg", "w").write(svg)
subprocess.run(["rsvg-convert", "/home/luke/Projects/design/san-marcos-deck/work/jb/draft/cor.svg", "-o", "/home/luke/Projects/design/san-marcos-deck/work/jb/draft/cor.png"], check=True)
