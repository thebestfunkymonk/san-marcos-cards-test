# for each ID: top-half at 750 before|after, plus 188 before|after upscaled x3 nearest
import sys, subprocess
from PIL import Image, ImageDraw
root = '/home/luke/Projects/design/san-marcos-deck'
R = root + '/build/review/courts2-kitreview'
for ID in sys.argv[1:]:
    b = Image.open(f'{root}/build/review/courts-before/png/{ID}.png').convert('RGB')
    subprocess.run(['rsvg-convert', '-w', '750', f'{root}/cards/{ID}.svg', '-o', f'{R}/a1_{ID}.png'], check=True)
    subprocess.run(['rsvg-convert', '-w', '188', f'{root}/cards/{ID}.svg', '-o', f'{R}/as_{ID}.png'], check=True)
    a = Image.open(f'{R}/a1_{ID}.png').convert('RGB')
    box = (139, 300, 611, 520)
    bc, ac = b.crop(box), a.crop(box)
    bs = Image.open(f'{root}/build/review/courts-before/small/{ID}.png').convert('RGB')
    as_ = Image.open(f'{R}/as_{ID}.png').convert('RGB')
    sbox = (30, 70, 158, 132)
    bs2 = bs.crop(sbox).resize(((sbox[2]-sbox[0])*3, (sbox[3]-sbox[1])*3), Image.NEAREST)
    as2 = as_.crop(sbox).resize(((sbox[2]-sbox[0])*3, (sbox[3]-sbox[1])*3), Image.NEAREST)
    W = bc.width * 2 + 10
    H = bc.height + 10 + bs2.height
    o = Image.new('RGB', (W, H), (128, 128, 128))
    o.paste(bc, (0, 0)); o.paste(ac, (bc.width + 10, 0))
    o.paste(bs2, (0, bc.height + 10)); o.paste(as2, (bc.width + 10, bc.height + 10))
    d = ImageDraw.Draw(o); d.text((4, 4), f'{ID} before 750 (y300-520)', fill=(255, 0, 255)); d.text((bc.width + 14, 4), 'after', fill=(255, 0, 255))
    d.text((4, bc.height + 14), '188 before (x3 nearest)', fill=(255, 0, 255))
    o.save(f'{R}/cs_{ID}.png')
