import re, subprocess, sys
from PIL import Image
def crop(src, vb, scale, out):
    s = open(src).read()
    s = re.sub(r'viewBox="[^"]*"', 'viewBox="%g %g %g %g"' % vb, s, count=1)
    s = re.sub(r'(<svg[^>]*?)\swidth="[^"]*"', r'\1 width="%d"' % round(vb[2] * scale), s, count=1)
    s = re.sub(r'(<svg[^>]*?)\sheight="[^"]*"', r'\1 height="%d"' % round(vb[3] * scale), s, count=1)
    # print view for the flat: drop non-printing dieline? keep
    fn = out.replace(".png", ".svg")
    open(fn, "w").write(s)
    subprocess.run(["rsvg-convert", "-b", "white", "-o", out, fn], check=True)
    return Image.open(out)
def side(imgs, out, pad=12):
    W = sum(i.width for i in imgs) + pad * (len(imgs) - 1); H = max(i.height for i in imgs)
    c = Image.new("RGB", (W, H), (255, 0, 255)); x = 0
    for i in imgs: c.paste(i.convert("RGB"), (x, 0)); x += i.width + pad
    c.save(out)
