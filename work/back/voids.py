"""Void map: jade inside the emblem limit farther than D px from any mark."""
import sys
sys.path.insert(0, '.')
import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt
import subprocess

def voidmap(svg_path, out, D=18.0):
    subprocess.run(['rsvg-convert', '-w', '750', svg_path, '-o', '/tmp/claude-1000/vm.png'], check=True)
    im = np.asarray(Image.open('/tmp/claude-1000/vm.png').convert('RGB')).astype(float)
    paper = (im.mean(axis=2) > 150)
    dist = distance_transform_edt(~paper)
    # lens interior (offset -12 like QA)
    from inkkit import geom as G
    from art import _back_geo as BG
    import shapely
    lim = BG.limit_region(margin=6.0)
    yy, xx = np.mgrid[0:1050, 0:750]
    inside = shapely.contains_xy(lim, xx + .5, yy + .5)
    v = (dist > D) & inside
    rgb = im.copy()
    rgb[v] = rgb[v] * 0.4 + np.array([230, 120, 40]) * 0.6
    Image.fromarray(rgb.astype(np.uint8)).save(out)
    print('void px (>%g from ink) inside lens: %d  max dist %.1f' % (D, v.sum(), dist[inside].max()))

if __name__ == '__main__':
    voidmap(sys.argv[1], sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else 18.0)
