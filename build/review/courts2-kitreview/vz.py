# vz.py ID cx cy half scale out  -> before|after side-by-side via viewBox crop (fast, any zoom)
import sys, re, subprocess, os, math
from PIL import Image, ImageDraw
ID, cx, cy, half, sc, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]), sys.argv[6]
root = '/home/luke/Projects/design/san-marcos-deck'
srcs = [(f'{root}/build/review/courts-before/cards/{ID}.svg', 'before'), (f'{root}/cards/{ID}.svg', 'after')]
if len(sys.argv) > 7:
    srcs = [(s, t) for s, t in srcs if t == sys.argv[7]]
tmpd = '/tmp/claude-1000/-home-luke-Projects-design/55d08c26-3490-4d22-8bb1-5d547fef47ba/scratchpad'
os.makedirs(tmpd, exist_ok=True)
x0, y0, W = cx - half, cy - half, 2 * half
pix = int(W * sc)
ims = []
for src, tag in srcs:
    s = open(src).read()
    s = re.sub(r'<svg([^>]*?)width="750" height="1050" viewBox="0 0 750 1050"',
               f'<svg\\1width="{pix}" height="{pix}" viewBox="{x0} {y0} {W} {W}"', s, count=1)
    p = f'{tmpd}/vz_{ID}_{tag}.svg'
    open(p, 'w').write(s)
    png = p[:-4] + '.png'
    subprocess.run(['rsvg-convert', p, '-o', png], check=True)
    im = Image.open(png).convert('RGB')
    d = ImageDraw.Draw(im)
    step = 5 if W <= 60 else 10
    for gx in range(int(math.ceil(x0 / step)) * step, int(x0 + W) + 1, step):
        X = (gx - x0) * sc; L = 14 if gx % 50 == 0 else 7
        d.line([(X, 0), (X, L)], fill=(255, 0, 255), width=2)
        if gx % (10 if W <= 60 else 50) == 0: d.text((X + 2, L), str(gx), fill=(255, 0, 255))
    for gy in range(int(math.ceil(y0 / step)) * step, int(y0 + W) + 1, step):
        Y = (gy - y0) * sc; L = 14 if gy % 50 == 0 else 7
        d.line([(0, Y), (L, Y)], fill=(255, 0, 255), width=2)
        if gy % (10 if W <= 60 else 50) == 0: d.text((L + 2, Y), str(gy), fill=(255, 0, 255))
    d.text((6, im.height - 14), f'{ID} {tag}', fill=(255, 0, 255))
    ims.append(im)
o = Image.new('RGB', (sum(i.width for i in ims) + 10 * (len(ims) - 1), ims[0].height), (128, 128, 128))
x = 0
for i in ims:
    o.paste(i, (x, 0)); x += i.width + 10
o.save(out)
