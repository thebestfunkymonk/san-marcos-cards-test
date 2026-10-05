"""zoom crops at QA-12 vector violations: python work/ac-followup/viol.py NAME"""
import sys, os, subprocess
sys.path.insert(0, os.getcwd())
from deck import qa as Q
from PIL import Image, ImageDraw
name = sys.argv[1]
svg = f"work/ac-followup/out/{name}/AC.svg"
pieces = Q.card_geometry(open(svg).read())
vec = Q.vector_gaps(pieces)
for v in vec:
    print(v["gap"], v["rule"], v["at"])
S = 8
big = f"work/ac-followup/out/{name}/AC_x{S}.png"
if not os.path.exists(big):
    subprocess.run(["rsvg-convert", "-w", str(750 * S), svg, "-o", big], check=True)
Image.MAX_IMAGE_PIXELS = None
im = Image.open(big)
seen = []
crops = []
for v in vec:
    x, y = v["at"]
    if any(abs(x - a) < 12 and abs(y - b) < 12 for a, b in seen):
        continue
    seen.append((x, y))
    c = im.crop((int((x - 20) * S), int((y - 20) * S), int((x + 20) * S), int((y + 20) * S))).convert("RGB")
    d = ImageDraw.Draw(c); d.ellipse((20 * S - 12, 20 * S - 12, 20 * S + 12, 20 * S + 12), outline="red", width=3)
    crops.append(c)
if crops:
    W = 320 * min(4, len(crops)); rows = (len(crops) + 3) // 4
    sheet = Image.new("RGB", (W, 320 * rows), "white")
    for i, c in enumerate(crops):
        sheet.paste(c, ((i % 4) * 320, (i // 4) * 320))
    sheet.save(f"work/ac-followup/out/{name}/viol.png"); print(f"work/ac-followup/out/{name}/viol.png")
