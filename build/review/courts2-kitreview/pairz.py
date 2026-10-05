# usage: pair.py ID cx cy half out [scale]
import sys
from PIL import Image, ImageDraw
R = '/home/luke/Projects/design/san-marcos-deck/build/review/courts2-kitreview'
ID, cx, cy, half, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), sys.argv[5]
S = int(sys.argv[6]) if len(sys.argv)>6 else 3
ims = []
for tag in ('b3', 'a3'):
    im = Image.open(f'{R}/{tag[0]}{S}/{ID}.png').convert('RGB')
    box = [int((cx-half)*S), int((cy-half)*S), int((cx+half)*S), int((cy+half)*S)]
    c = im.crop(box)
    d = ImageDraw.Draw(c)
    # grid ticks every 10 card px
    x0, y0 = cx-half, cy-half
    import math
    for gx in range(int(math.ceil(x0/10))*10, int(cx+half)+1, 10):
        X = (gx-x0)*S
        L = 14 if gx % 50 == 0 else 6
        d.line([(X,0),(X,L)], fill=(255,0,255), width=2)
        if gx % 50 == 0: d.text((X+2, L), str(gx), fill=(255,0,255))
    for gy in range(int(math.ceil(y0/10))*10, int(cy+half)+1, 10):
        Y = (gy-y0)*S
        L = 14 if gy % 50 == 0 else 6
        d.line([(0,Y),(L,Y)], fill=(255,0,255), width=2)
        if gy % 50 == 0: d.text((L+2, Y), str(gy), fill=(255,0,255))
    d.text((6, c.height-14), f'{ID} {"before" if tag=="b3" else "after"}', fill=(255,0,255))
    ims.append(c)
W = ims[0].width*2 + 10
out_im = Image.new('RGB', (W, ims[0].height), (128,128,128))
out_im.paste(ims[0], (0,0)); out_im.paste(ims[1], (ims[0].width+10, 0))
out_im.save(out)
