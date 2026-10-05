"""Quick look: line-mode render of the back parts (paper on jade), coverage estimate.
usage: quick.py OUT_PREFIX [--only a,b] [--w 750]"""
import sys, os, subprocess, time, importlib
sys.path.insert(0, '.')
import numpy as np
from deck import tokens as T
from art import _back_frame as BF
import art.BACK as BACK

def main():
    out = sys.argv[1]
    only = None
    pre = None
    for a in sys.argv[2:]:
        if a.startswith('--only='):
            only = a.split('=', 1)[1].split(',')
        if a.startswith('--pre='):
            pre = a.split('=', 1)[1]
    if pre:
        exec(pre, globals())
    t = time.time()
    parts = BACK.parts()
    print('parts %.1fs' % (time.time() - t))
    body = [f'<path d="{BF.flood_d()}" fill="{T.JADE}"/>']
    for k, f in parts.items():
        if only and k not in only:
            continue
        s = f.recolor(T.PAPER).svg()
        body.append(f'<g id="{k}">{s}</g>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 750 1050" width="750" height="1050">'
           f'<rect width="750" height="1050" rx="37.5" fill="{T.PAPER}"/>' + "".join(body) + '</svg>')
    open(out + '.svg', 'w').write(svg)
    subprocess.run(['rsvg-convert', '-w', '750', out + '.svg', '-o', out + '.png'], check=True)
    subprocess.run(['rsvg-convert', '-w', '188', out + '.svg', '-o', out + '-188.png'], check=True)
    subprocess.run(['rsvg-convert', '-w', '1500', out + '.svg', '-o', out + '-1500.png'], check=True)
    # coverage at 2x
    subprocess.run(['rsvg-convert', '-w', '1500', out + '.svg', '-o', '/tmp/claude-1000/qcov.png'], check=True)
    from PIL import Image
    im = np.asarray(Image.open('/tmp/claude-1000/qcov.png').convert('RGB')).astype(float)
    jade = np.array([int(T.JADE[i:i+2], 16) for i in (1, 3, 5)], float)
    paper = np.array([int(T.PAPER[i:i+2], 16) for i in (1, 3, 5)], float)
    sub = im[75:2025, 75:1425]
    # fraction toward paper along jade->paper
    v = ((sub - jade) @ (paper - jade)) / ((paper - jade) @ (paper - jade))
    v = np.clip(v, 0, 1)
    print('coverage ~ %.2f%%' % (v.mean() * 100))
    for k, f in parts.items():
        print(f'  {k:10s} {f.shape().area/657000*100:5.2f}%')

main()
