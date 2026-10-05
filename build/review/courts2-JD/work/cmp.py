"""cmp.py out.png x y w h scale tag1 tag2 ...  -> side-by-side zooms of out/<tag>/JD.svg"""
import sys, subprocess, os
from PIL import Image, ImageDraw
W = 'build/review/courts2-JD/work'
out, x, y, w, h, s, *tags = sys.argv[1:]
ims = []
for t in tags:
    svg = t if t.endswith('.svg') else f'{W}/out/{t}/JD.svg'
    o = f'{W}/out/_z_{os.getpid()}_{len(ims)}.png'
    subprocess.run(['bash', f'{W}/zoom.sh', svg, x, y, w, h, s, o, 'g'], check=True)
    ims.append(Image.open(o).convert('RGB')); os.remove(o)
pad = 10
im = Image.new('RGB', (sum(i.width for i in ims) + pad * (len(ims) - 1), max(i.height for i in ims) + 20), 'white')
d = ImageDraw.Draw(im); xx = 0
for t, i in zip(tags, ims):
    im.paste(i, (xx, 20)); d.text((xx + 4, 4), os.path.basename(os.path.dirname(t)) if t.endswith('.svg') else t, fill='black'); xx += i.width + pad
im.save(out)
