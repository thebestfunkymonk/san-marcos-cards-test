import subprocess, os
from PIL import Image, ImageDraw, ImageFont
R = '/home/luke/Projects/design/san-marcos-deck'
M = R + '/build/review/courts2-JH/montage'
B = R + '/build/review/courts-before'
os.makedirs(M, exist_ok=True)
def flat(p):
    im = Image.open(p).convert('RGBA'); bg = Image.new('RGBA', im.size, 'white'); bg.alpha_composite(im); return bg.convert('RGB')
subprocess.run(['rsvg-convert', '-w', '2250', B + '/cards/JH.svg', '-o', M + '/before3x.png'], check=True)
subprocess.run(['rsvg-convert', '-w', '2250', R + '/cards/JH.svg', '-o', M + '/after3x.png'], check=True)
b3, a3 = flat(M + '/before3x.png'), flat(M + '/after3x.png')
def flat(p):
    im = Image.open(p).convert('RGBA'); bg = Image.new('RGBA', im.size, 'white'); bg.alpha_composite(im); return bg.convert('RGB')
b750, a750 = flat(B + '/png/JH.png'), flat(R + '/build/png/JH.png')
b188, a188 = flat(B + '/small/JH.png'), flat(R + '/build/png/small/JH.png')
try:
    F = ImageFont.truetype('/usr/share/fonts/TTF/DejaVuSans.ttf', 22)
    FS = ImageFont.truetype('/usr/share/fonts/TTF/DejaVuSans.ttf', 16)
except Exception:
    F = FS = ImageFont.load_default()

def crop3(img, x, y, w, h, scale=1.0):
    c = img.crop((int(x * 3), int(y * 3), int((x + w) * 3), int((y + h) * 3)))
    if scale != 1.0:
        c = c.resize((int(c.width * scale), int(c.height * scale)), Image.LANCZOS)
    return c

def pair(name, x, y, w, h, scale=1.0):
    bb, aa = crop3(b3, x, y, w, h, scale), crop3(a3, x, y, w, h, scale)
    bb.save(f'{M}/{name}_before.png'); aa.save(f'{M}/{name}_after.png')
    return bb, aa

def labelled(pairs, title):
    """pairs: list of (label, before, after) -> one block, before over after per column."""
    pad = 12
    colw = [max(b.width, a.width) for _, b, a in pairs]
    hb = max(b.height for _, b, _ in pairs); ha = max(a.height for _, _, a in pairs)
    W = sum(colw) + pad * (len(pairs) + 1) + 90
    H = 40 + 28 + hb + pad + ha + pad
    im = Image.new('RGB', (W, H), 'white'); d = ImageDraw.Draw(im)
    d.text((pad, 8), title, fill='black', font=F)
    d.text((pad, 68 + hb // 2), 'before', fill='black', font=FS)
    d.text((pad, 68 + hb + pad + ha // 2), 'after', fill='black', font=FS)
    x = 90
    for (lab, b, a), cw in zip(pairs, colw):
        d.text((x, 42), lab, fill='black', font=FS)
        im.paste(b, (x, 68)); im.paste(a, (x, 68 + hb + pad))
        x += cw + pad
    return im

# row 1: 750 + 188
pad = 16
r1 = Image.new('RGB', (750 * 2 + 188 * 2 + pad * 5, 1050 + 60), 'white'); d = ImageDraw.Draw(r1)
d.text((pad, 10), 'JH (Jack of Hearts) - before (left) / after (right): 750 px and 188 px', fill='black', font=F)
r1.paste(b750, (pad, 50)); r1.paste(a750, (750 + 2 * pad, 50))
r1.paste(b188, (1500 + 3 * pad, 50)); r1.paste(a188, (1500 + 188 + 4 * pad, 50))
# 188 ×2 (nearest) under the 188s
b2 = b188.resize((188 * 2 // 1, 263 * 2), Image.NEAREST) if False else None
r1.save(M + '/row1_750_188.png')

hands = [('bow hand (fig. R) 3x',) + pair('handL', 200, 385, 105, 125),
         ('fiddle hand (fig. L) 3x',) + pair('handR', 495, 220, 100, 115),
         ('fiddle hand, 180 copy 3x',) + pair('handR180', 155, 715, 100, 115)]
r2 = labelled(hands, 'Hands at 3x (card px x3)')
r2.save(M + '/row2_hands.png')

others = [('frog top / button / heel pocket',) + pair('frog', 228, 436, 70, 72),
          ('fingertips / sleeve edge',) + pair('tips', 268, 396, 44, 56),
          ('cuff / upper bout',) + pair('cuffbout', 528, 268, 62, 58),
          ('brooch',) + pair('brooch', 352, 132, 64, 60),
          ('beret underside',) + pair('beret', 438, 132, 58, 52)]
r3 = labelled(others, 'Hand-adjacent and head fixes at 3x')
r3.save(M + '/row3_other.png')
others2 = [('plume tip',) + pair('plume', 495, 68, 82, 52),
           ('right edge (red chip)',) + pair('redge', 560, 395, 52, 90),
           ('band: bulb / bead',) + pair('band', 330, 470, 100, 45),
           ('sleeve / band',) + pair('sleeveband', 158, 470, 60, 45)]
r4 = labelled(others2, 'Other fixes at 3x')
r4.save(M + '/row4_other.png')

W = max(r1.width, r2.width, r3.width, r4.width)
out = Image.new('RGB', (W, r1.height + r2.height + r3.height + r4.height), 'white')
y = 0
for r in (r1, r2, r3, r4):
    out.paste(r, (0, y)); y += r.height
out.save(R + '/build/review/courts2-JH/before-after.png')
print(out.size)
