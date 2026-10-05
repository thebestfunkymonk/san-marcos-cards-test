import subprocess, os
from PIL import Image, ImageDraw, ImageFont
R = '/home/luke/Projects/design/san-marcos-deck'
M = R + '/build/review/courts2-JD/montage'
B = R + '/build/review/courts-before'
os.makedirs(M, exist_ok=True)


def flat(p):
    im = Image.open(p).convert('RGBA'); bg = Image.new('RGBA', im.size, 'white'); bg.alpha_composite(im)
    return bg.convert('RGB')


subprocess.run(['rsvg-convert', '-w', '2250', B + '/cards/JD.svg', '-o', M + '/before3x.png'], check=True)
subprocess.run(['rsvg-convert', '-w', '2250', R + '/cards/JD.svg', '-o', M + '/after3x.png'], check=True)
b3, a3 = flat(M + '/before3x.png'), flat(M + '/after3x.png')
b750, a750 = flat(B + '/png/JD.png'), flat(R + '/build/png/JD.png')
b188, a188 = flat(B + '/small/JD.png'), flat(R + '/build/png/small/JD.png')
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


pad = 16
# row 1: 750 and 188 (188 also shown 2x nearest so it can be judged)
b2, a2 = b188.resize((376, b188.height * 2), Image.NEAREST), a188.resize((376, a188.height * 2), Image.NEAREST)
r1 = Image.new('RGB', (750 * 2 + 188 * 2 + 376 * 2 + pad * 7, 1050 + 60), 'white'); d = ImageDraw.Draw(r1)
d.text((pad, 10), 'JD (Jack of Diamonds) - before | after at 750 px;  188 px before | after;  188 px x2 (nearest) before | after',
       fill='black', font=F)
x = pad
for im in (b750, a750, b188, a188):
    r1.paste(im, (x, 50)); x += im.width + pad
r1.paste(b2, (x, 50)); r1.paste(a2, (x, 50 + b2.height + pad))
r1.save(M + '/row1_750_188.png')

hands = [('trumpet hand (fig. L) 3x',) + pair('handR', 405, 345, 115, 105),
         ('map hand (fig. R) 3x',) + pair('handL', 190, 420, 110, 91),
         ('trumpet hand, 180 copy 3x',) + pair('handR180', 230, 600, 115, 105)]
r2 = labelled(hands, 'Hands at 3x (card px x3)')
r2.save(M + '/row2_hands.png')

others = [('eyes',) + pair('eyes', 350, 198, 80, 28),
          ('band / far lock / brooch',) + pair('band', 330, 160, 115, 36),
          ('map: route across the river, chain',) + pair('map', 262, 400, 120, 111),
          ('roller / buckle',) + pair('buckle', 350, 425, 70, 60)]
r3 = labelled(others, 'Face, cap and map fixes at 3x')
r3.save(M + '/row3_other.png')
others2 = [('belt volute / right cuff',) + pair('belt', 405, 430, 85, 55),
           ('chain rails at the band',) + pair('rails', 455, 460, 70, 51),
           ('left cuff at the band',) + pair('cuffL', 185, 470, 75, 41)]
r4 = labelled(others2, 'Other fixes at 3x')
r4.save(M + '/row4_other.png')

rows = [r1, r2, r3, r4]
W = max(r.width for r in rows); H = sum(r.height for r in rows) + pad * (len(rows) + 1)
out = Image.new('RGB', (W, H), 'white'); y = pad
for r in rows:
    out.paste(r, (0, y)); y += r.height + pad
out.save(R + '/build/review/courts2-JD/before-after.png')
print(out.size)
