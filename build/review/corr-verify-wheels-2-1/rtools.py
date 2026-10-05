"""verifier helpers: crop renders of SVGs via rsvg-convert."""
import re, subprocess, tempfile, os, io
import numpy as np
from PIL import Image

def crop_svg(svg_text, box, scale, keep=None, drop_stock=False):
    x0, y0, x1, y1 = box
    t = svg_text
    t = re.sub(r'(<svg[^>]*?)\swidth="[^"]*"', r'\1', t, count=1)
    t = re.sub(r'(<svg[^>]*?)\sheight="[^"]*"', r'\1', t, count=1)
    t = re.sub(r'viewBox="[^"]*"', f'viewBox="{x0} {y0} {x1-x0} {y1-y0}" width="{(x1-x0)*scale:.0f}" height="{(y1-y0)*scale:.0f}"', t, count=1)
    if drop_stock:
        t = re.sub(r'<path[^>]*class="stock"[^>]*/>', '', t)
    if keep is not None:
        # keep only top-level <g id=...> in keep
        def repl(m):
            return m.group(0) if m.group(1) in keep else ''
        t = re.sub(r'<g id="([^"]+)"[^>]*>.*?</g>\s*(?=<g id=|</svg>)', repl, t, flags=re.S)
    return t

def render(svg_text, box, scale, **kw):
    t = crop_svg(svg_text, box, scale, **kw)
    with tempfile.NamedTemporaryFile('w', suffix='.svg', delete=False) as f:
        f.write(t); p = f.name
    out = subprocess.run(['rsvg-convert', p], capture_output=True, check=True).stdout
    os.unlink(p)
    return Image.open(io.BytesIO(out)).convert('RGBA')

def side_by_side(imgs, labels=None, pad=8, bg=(255, 255, 255, 255)):
    from PIL import ImageDraw
    h = max(i.height for i in imgs) + (18 if labels else 0)
    w = sum(i.width for i in imgs) + pad * (len(imgs) - 1)
    out = Image.new('RGBA', (w, h), bg)
    x = 0
    d = ImageDraw.Draw(out)
    for k, i in enumerate(imgs):
        out.paste(i, (x, 18 if labels else 0), i)
        if labels:
            d.text((x + 4, 2), labels[k], fill=(0, 0, 0, 255))
        x += i.width + pad
    return out
