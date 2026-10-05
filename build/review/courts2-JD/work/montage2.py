"""Round-2 before/after montage for J♦.

before  = the pre-review snapshot (build/review/courts-before: png 750, small 188, cards/JD.svg for crops)
round 1 = the round-1 final (work/r2_start/JD.svg) — shown for the verifier's items only
after   = cards/JD.svg / build/png (current)
Writes build/review/courts2-JD/before-after.png (crops in build/review/courts2-JD/montage/)."""
import os
import subprocess

from PIL import Image, ImageDraw, ImageFont

R = '/home/luke/Projects/design/san-marcos-deck'
Wd = R + '/build/review/courts2-JD/work'
M = R + '/build/review/courts2-JD/montage'
B = R + '/build/review/courts-before'
os.makedirs(M, exist_ok=True)
SV = {'before': B + '/cards/JD.svg', 'round 1': Wd + '/r2_start/JD.svg', 'after': R + '/cards/JD.svg'}
try:
    F = ImageFont.truetype('/usr/share/fonts/noto/NotoSans-Regular.ttf', 22)
    FS = ImageFont.truetype('/usr/share/fonts/noto/NotoSans-Regular.ttf', 16)
except Exception:
    F = FS = ImageFont.load_default()


def flat(p):
    im = Image.open(p).convert('RGBA')
    bg = Image.new('RGBA', im.size, 'white')
    bg.alpha_composite(im)
    return bg.convert('RGB')


def zoom(tag, name, x, y, w, h, s):
    out = f'{M}/{name}_{tag.replace(" ", "")}.png'
    subprocess.run(['bash', Wd + '/zoom.sh', SV[tag], str(x), str(y), str(w), str(h), str(s), out], check=True)
    return flat(out)


# the left hand / map group moved between states: its crops follow it (offsets from the 'after' position)
FOLLOW_L = {'before': (12.0, 14.0), 'round 1': (9.0, 8.0), 'after': (0.0, 0.0)}


def row(items, title, tags=('before', 'after')):
    """items: (label, name, x, y, w, h, scale[, follow]); one column per item, one line per tag."""
    pad = 12
    cols = [[zoom(t, it[1], it[2] + (FOLLOW_L[t][0] if len(it) > 7 else 0.0),
                  it[3] + (FOLLOW_L[t][1] if len(it) > 7 else 0.0), *it[4:7]) for t in tags] for it in items]
    colw = [max(c.width for c in cs) for cs in cols]
    rh = [max(cs[k].height for cs in cols) for k in range(len(tags))]
    Wt = sum(colw) + pad * (len(cols) + 1) + 90
    Ht = 40 + 28 + sum(rh) + pad * len(tags)
    im = Image.new('RGB', (Wt, Ht), 'white')
    d = ImageDraw.Draw(im)
    d.text((pad, 8), title, fill='black', font=F)
    yy = 68
    for k, t in enumerate(tags):
        d.text((pad, yy + rh[k] // 2), t, fill='black', font=FS)
        yy += rh[k] + pad
    xx = 90
    for (lab, *_), cs, cw in zip(items, cols, colw):  # noqa: B007
        d.text((xx, 42), lab, fill='black', font=FS)
        yy = 68
        for k, c in enumerate(cs):
            im.paste(c, (xx, yy))
            yy += rh[k] + pad
        xx += cw + pad
    return im


pad = 16
b750, a750 = flat(B + '/png/JD.png'), flat(R + '/build/png/JD.png')
b188, a188 = flat(B + '/small/JD.png'), flat(R + '/build/png/small/JD.png')
b2, a2 = b188.resize((376, b188.height * 2), Image.NEAREST), a188.resize((376, a188.height * 2), Image.NEAREST)
r1 = Image.new('RGB', (750 * 2 + 188 * 2 + 376 + pad * 6, 1050 + 60), 'white')
d = ImageDraw.Draw(r1)
d.text((pad, 10), 'JD (Jack of Diamonds) round 2: before (pre-review) | after at 750 px;  188 px before | after;  188 px ×2 before / after',
       fill='black', font=F)
x = pad
for im in (b750, a750, b188, a188):
    r1.paste(im, (x, 50))
    x += im.width + pad
r1.paste(b2, (x, 50))
r1.paste(a2, (x, 50 + b2.height + pad))

hands = [('trumpet hand (fig. L) 3×', 'handR', 405, 345, 115, 105, 3),
         ('map hand (fig. R) 3×', 'handL', 185, 415, 115, 100, 3),
         ('trumpet hand, 180° copy 3×', 'handR180', 230, 600, 115, 105, 3),
         ('map hand, 180° copy 3×', 'handL180', 450, 535, 115, 100, 3)]
r2 = row(hands, 'Hands at 3× (before = pre-review, after = now)')
close = [('R thumb tip vs index 10×', 'thumbR', 428, 364, 36, 30, 10),
         ('L thumb, roll edge 10× (follows the hand)', 'thumbL', 236, 426, 44, 32, 10, 1),
         ('R heel junction 14×', 'heelR', 436, 405, 26, 22, 14),
         ('L heel into the cuff 8× (follows)', 'heelL', 196, 455, 50, 35, 8, 1)]
r3 = row(close, 'Hand close-ups (verifier: thumb knot, 1 px heel jog)', tags=('before', 'round 1', 'after'))
items = [('L cuff sprig (regression) 8× (follows)', 'cuffL', 176, 466, 62, 46, 8, 1),
         ('R rim beside the fist 8×', 'rim', 462, 370, 40, 58, 8),
         ('R forearm × tabard edge 5×', 'forearm', 440, 440, 80, 72, 5),
         ('belt stem / cuff sprig 8×', 'beltcuff', 430, 438, 50, 42, 8)]
r4 = row(items, 'Verifier items (1)', tags=('before', 'round 1', 'after'))
items2 = [('roll ends / tabard edge 5×', 'roll', 244, 412, 64, 96, 5),
          ('map river + route 4×', 'map', 262, 420, 112, 80, 4),
          ('near pupil 20×', 'eye', 366, 204, 16, 12, 20),
          ('collar / V-neck corner 10×', 'collar', 400, 286, 36, 32, 10),
          ('cuff top corners 12×', 'cuffcorner', 470, 408, 30, 24, 12)]
r5 = row(items2, 'Verifier items (2) and other fixes', tags=('before', 'round 1', 'after'))

rows = [r1, r2, r3, r4, r5]
Wt = max(r.width for r in rows)
Ht = sum(r.height for r in rows) + pad * (len(rows) + 1)
out = Image.new('RGB', (Wt, Ht), 'white')
y = pad
for r in rows:
    out.paste(r, (0, y))
    y += r.height + pad
out.save(R + '/build/review/courts2-JD/before-after.png')
for k, r in enumerate(rows, 1):
    r.save(f'{M}/r2_row{k}.png')
print(out.size)
