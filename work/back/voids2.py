"""Void map over the whole flood: jade farther than D px from any paper line."""
import sys
sys.path.insert(0, '.')
import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt
import subprocess

def voidmap(svg_path, out, D=14.0):
    subprocess.run(['rsvg-convert', '-w', '750', svg_path, '-o', '/tmp/claude-1000/vm.png'], check=True)
    im = np.asarray(Image.open('/tmp/claude-1000/vm.png').convert('RGB')).astype(float)
    paper = (im.mean(axis=2) > 150)
    dist = distance_transform_edt(~paper)
    v = (dist > D)
    rgb = im.copy()
    rgb[v] = rgb[v] * 0.4 + np.array([230, 120, 40]) * 0.6
    Image.fromarray(rgb.astype(np.uint8)).save(out)
    print('void px (>%g): %d' % (D, v.sum()))

voidmap(sys.argv[1], sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else 14.0)
