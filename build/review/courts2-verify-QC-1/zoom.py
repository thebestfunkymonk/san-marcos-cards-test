import re, subprocess, sys
# usage: zoom.py name x0 y0 x1 y1 scale
name, x0, y0, x1, y1, s = sys.argv[1], *map(float, sys.argv[2:7])
V = "build/review/courts2-verify-QC-1"
outs = []
for tag, src in (("B", "build/review/courts-before/cards/QC.svg"), ("A", "cards/QC.svg")):
    t = open(src).read()
    w, h = (x1 - x0) * s, (y1 - y0) * s
    t = re.sub(r'<svg([^>]*?)width="750" height="1050" viewBox="0 0 750 1050"',
               lambda m: f'<svg{m.group(1)}width="{w:.0f}" height="{h:.0f}" viewBox="{x0} {y0} {x1-x0} {y1-y0}"', t, count=1)
    p = f"{V}/_z_{tag}.svg"
    open(p, "w").write(t)
    o = f"{V}/{tag}_{name}.png"
    subprocess.run(["rsvg-convert", p, "-o", o], check=True)
    outs.append(o)
subprocess.run(["magick", *outs, "-background", "#ff00ff", "-splice", "4x0", "+append", f"{V}/cmp_{name}.png"], check=True)
print(f"{V}/cmp_{name}.png")
