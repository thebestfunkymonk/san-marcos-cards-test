import os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
ROOT = '/home/luke/Projects/design/san-marcos-deck'
M = ROOT + '/build/review/courts2-KH/mont2'
SV = {'before': ROOT + '/build/review/courts-before/cards/KH.svg', 'round 1': M + '/r1.svg', 'after': ROOT + '/cards/KH.svg'}
PNG = {'before': ROOT + '/build/review/courts-before/png/KH.png', 'round 1': M + '/r1.png', 'after': ROOT + '/build/png/KH.png'}
SM = {'before': ROOT + '/build/review/courts-before/small/KH.png', 'round 1': M + '/r1-188.png', 'after': ROOT + '/build/png/small/KH.png'}
cache = {}
def full(k, S):
    key = (k, S)
    if key not in cache:
        out = f'{M}/_{k.replace(" ", "")}_{S}.png'
        subprocess.run(['rsvg-convert', '-w', str(int(750 * S)), SV[k], '-o', out], check=True)
        cache[key] = Image.open(out).convert('RGB')
    return cache[key]
def crop(k, box, S):
    x0, y0, x1, y1 = box
    return full(k, S).crop((int(x0 * S), int(y0 * S), int(x1 * S), int(y1 * S)))
try:
    font = ImageFont.truetype('/usr/share/fonts/noto/NotoSans-Regular.ttf', 22)
    fsm = ImageFont.truetype('/usr/share/fonts/noto/NotoSans-Regular.ttf', 18)
except Exception:
    font = fsm = ImageFont.load_default()
def row(title, ims, labels, pad=10):
    h = max(i.height for i in ims) + 34
    w = sum(i.width for i in ims) + pad * (len(ims) + 1)
    r = Image.new('RGB', (w, h + 32), (136, 136, 136))
    d = ImageDraw.Draw(r)
    d.text((pad, 4), title, fill=(255, 255, 255), font=font)
    x = pad
    for im, lb in zip(ims, labels):
        d.text((x, 34), lb, fill=(255, 255, 255), font=fsm)
        r.paste(im, (x, 60))
        x += im.width + pad
    return r
K3 = ['before', 'round 1', 'after']
rows = []
# 750 and 188
rows.append(row('KH at 750 px', [Image.open(PNG[k]).convert('RGB') for k in ('before', 'after')], ['before', 'after (round 2)']))
sm = [Image.open(SM[k]).convert('RGB') for k in K3]
sm = [i.resize((i.width * 2, i.height * 2), Image.NEAREST) for i in sm] + [Image.open(SM[k]).convert('RGB') for k in ('before', 'after')]
rows.append(row('188 px (x2 nearest, then x1)', sm, ['before x2', 'round 1 x2', 'after x2', 'before', 'after']))
boxes = [
    ('chalice hand 3x', (160, 345, 300, 470), 3),
    ('pole hand 3x', (465, 395, 611, 511), 3),
    ('chalice hand 6x', (175, 355, 285, 455), 6),
    ('pole hand 6x', (480, 405, 590, 505), 6),
    ('left cuff vs robe contour 10x (verifier: contour on the cuff corner)', (145, 395, 215, 465), 10),
    ('right cuff vs robe contour 10x', (545, 425, 611, 495), 10),
    ('crown / pole 6x (verifier: pearl bump, knot at post foot)', (285, 95, 355, 160), 6),
    ('stem ends on the chalice fist 12x (verifier: cap nubs)', (222, 366, 258, 390), 12),
    ('pole ends on the pole fist 12x', (502, 420, 538, 450), 12),
    ('right lapel lens beside the pole 6x (verifier: free caps)', (410, 268, 490, 372), 6),
]
for t, b, S in boxes:
    rows.append(row(t, [crop(k, b, S) for k in K3], K3))
W = max(r.width for r in rows)
H = sum(r.height for r in rows)
out = Image.new('RGB', (W, H), (110, 110, 110))
y = 0
for r in rows:
    out.paste(r, (0, y)); y += r.height
out.save(ROOT + '/build/review/courts2-KH/before-after.png')
print(out.size)
# a smaller overview for looking
