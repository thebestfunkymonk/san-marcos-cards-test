"""crops.py <svg> <out.png> x0,y0,x1,y1 [...] : 8x crops (padded 12 px) of card-px boxes, appended."""
import sys, subprocess, os
svg, out = sys.argv[1], sys.argv[2]
S = 8
big = out + ".big.png"
subprocess.run(["rsvg-convert", "-w", str(750 * S), svg, "-o", big], check=True)
parts = []
for i, b in enumerate(sys.argv[3:]):
    x0, y0, x1, y1 = map(float, b.split(","))
    x0, y0, x1, y1 = x0 - 12, y0 - 12, x1 + 12, y1 + 12
    p = f"{out}.{i}.png"
    subprocess.run(["magick", big, "-crop", f"{int((x1-x0)*S)}x{int((y1-y0)*S)}+{int(x0*S)}+{int(y0*S)}", "+repage",
                    "-bordercolor", "red", "-border", "3", p], check=True)
    parts.append(p)
subprocess.run(["magick"] + parts + ["+append", out], check=True)
for p in parts + [big]:
    os.remove(p)
