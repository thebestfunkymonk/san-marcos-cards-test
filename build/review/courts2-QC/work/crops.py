"""crops.py SVG OUTPREFIX [names...]: named close-up crops of Q♣."""
import subprocess, sys, os, tempfile
svg, pre = sys.argv[1], sys.argv[2]
want = sys.argv[3:]
CROPS = {  # name: (x0, y0, x1, y1, zoom)
    "hL": (262, 368, 362, 468, 6), "hR": (496, 388, 586, 488, 6),
    "hL12": (290, 380, 350, 440, 12), "hR12": (505, 400, 565, 460, 12),
    "wristL": (270, 430, 340, 490, 10), "wristR": (495, 440, 555, 500, 10),
    "knop": (510, 262, 575, 305, 10), "parting": (360, 140, 410, 175, 12),
    "ferrule": (280, 355, 330, 395, 12), "face": (330, 150, 450, 290, 5),
    "crown": (310, 60, 460, 170, 5), "top": (139, 55, 611, 511, 3),
    "cloakR": (520, 280, 611, 511, 4), "cloakL": (139, 280, 250, 511, 4),
    "chest": (300, 280, 460, 511, 4), "fan": (160, 220, 340, 420, 4),
}
tmp = {}
def full(z):
    if z not in tmp:
        fd, p = tempfile.mkstemp(suffix=".png"); os.close(fd)
        subprocess.run(["rsvg-convert", "-w", str(int(750 * z)), svg, "-o", p], check=True)
        tmp[z] = p
    return tmp[z]
for nm, (x0, y0, x1, y1, z) in CROPS.items():
    if want and nm not in want:
        continue
    g = f"{int((x1-x0)*z)}x{int((y1-y0)*z)}+{int(x0*z)}+{int(y0*z)}"
    subprocess.run(["magick", full(z), "-crop", g, "+repage", f"{pre}_{nm}.png"], check=True)
for p in tmp.values():
    os.remove(p)
