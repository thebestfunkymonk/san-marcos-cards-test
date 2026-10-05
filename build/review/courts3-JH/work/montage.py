import subprocess, os
from PIL import Image, ImageDraw, ImageFont
R = '/home/luke/Projects/design/san-marcos-deck'
O = R + '/build/review/courts3-JH'
M = O + '/montage'
B = R + '/build/review/courts-before'
os.makedirs(M, exist_ok=True)
def flat(p):
    im = Image.open(p).convert('RGBA'); bg = Image.new('RGBA', im.size, 'white'); bg.alpha_composite(im); return bg.convert('RGB')
subprocess.run(['rsvg-convert', '-w', '2250', B + '/cards/JH.svg', '-o', M + '/before3x.png'], check=True)
subprocess.run(['rsvg-convert', '-w', '2250', R + '/cards/JH.svg', '-o', M + '/after3x.png'], check=True)
subprocess.run(['rsvg-convert', '-w', '2250', O + '/work/base/JH.svg', '-o', M + '/start3x.png'], check=True)
b3, a3 = flat(M + '/before3x.png'), flat(M + '/after3x.png')
s3 = flat(M + '/start3x.png')
b750, a750 = flat(B + '/png/JH.png'), flat(R + '/build/png/JH.png')
b188, a188 = flat(B + '/small/JH.png'), flat(R + '/build/png/small/JH.png')
F = ImageFont.truetype('/usr/share/fonts/noto/NotoSans-Regular.ttf', 24)
FS = ImageFont.truetype('/usr/share/fonts/noto/NotoSans-Regular.ttf', 17)

def crop3(img, x, y, w, h, scale=1.0):
    c = img.crop((int(x * 3), int(y * 3), int((x + w) * 3), int((y + h) * 3)))
    if scale != 1.0:
        c = c.resize((int(c.width * scale), int(c.height * scale)), Image.NEAREST)
    return c

def pair(x, y, w, h, scale=1.0, pre=None):
    """(pre-review, round start, after) crops; ``pre`` = (x, y) where the feature sat before the review."""
    px, py = pre if pre is not None else (x, y)
    return crop3(b3, px, py, w, h, scale), crop3(s3, x, y, w, h, scale), crop3(a3, x, y, w, h, scale)

def labelled(cols, title, W=None):
    pad = 14
    colw = [max(im.width for im in c[1:]) for c in cols]
    hs = [max(c[k].height for c in cols) for k in (1, 2, 3)]
    Wc = sum(colw) + pad * (len(cols) + 1) + 130
    H = 44 + 30 + sum(hs) + 3 * pad
    im = Image.new('RGB', (max(Wc, W or 0), H), 'white'); d = ImageDraw.Draw(im)
    d.text((pad, 8), title, fill='black', font=F)
    ys = [74, 74 + hs[0] + pad, 74 + hs[0] + hs[1] + 2 * pad]
    for lab, y, h in zip(('pre-review', 'round start', 'after'), ys, hs):
        d.text((pad, y + h // 2 - 10), lab, fill='black', font=FS)
    x = 130
    for c, cw in zip(cols, colw):
        d.text((x, 46), c[0], fill='black', font=FS)
        for img, y in zip(c[1:], ys):
            im.paste(img, (x, y))
        x += cw + pad
    return im

pad = 16
r1 = Image.new('RGB', (750 * 2 + 188 * 2 + pad * 5, 1050 + 60), 'white'); d = ImageDraw.Draw(r1)
d.text((pad, 12), 'J♥ Spring Minstrel - before (pre-review) | after (courts3 r1): 750 px and 188 px', fill='black', font=F)
r1.paste(b750, (pad, 50)); r1.paste(a750, (750 + 2 * pad, 50))
r1.paste(b188, (1500 + 3 * pad, 50)); r1.paste(a188, (1500 + 188 + 4 * pad, 50))
W = r1.width
rows = [r1]
rows.append(labelled([
    ('1 neck/body joint 6x', *pair(505, 272, 50, 36, 2.0)),
    ('2 shoulder x bow 3x', *pair(236, 286, 70, 50, 1.4)),
    ('3 heel pocket 3x', *pair(228, 440, 50, 66, 1.4)),
    ('fiddle-bout / sleeve edge 3x', *pair(440, 420, 60, 90, 1.0)),
], 'Open issues 1-3 (+ the sleeve edge that ran 1.1 px off the lower bout: heal had cut the body outline)', W))
rows.append(labelled([
    ('4 fiddle fist 3x', *pair(495, 222, 64, 60, 1.6, pre=(495, 248))),
    ('4 fiddle fist top-left 3x', *pair(508, 230, 26, 22, 3.0, pre=(510, 259))),
    ('4 fiddle pinky/neck 3x', *pair(508, 260, 26, 20, 3.0, pre=(510, 284))),
    ('4 bow fist 3x', *pair(232, 396, 62, 52, 1.6, pre=(234, 394))),
    ('4 bow thumb/stick 3x', *pair(256, 400, 24, 18, 3.0, pre=(262, 396))),
], 'Issue 4: thumb / index / neck knots and the fist-bottom step, both fists', W))
H = sum(r.height for r in rows)
out = Image.new('RGB', (max(r.width for r in rows), H), 'white')
y = 0
for r in rows:
    out.paste(r, (0, y)); y += r.height
out.save(O + '/before-after.png')
print(out.size)
