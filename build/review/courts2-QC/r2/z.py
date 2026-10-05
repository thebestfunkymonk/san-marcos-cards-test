"""z.py OUT svg x0 y0 x1 y1 scale [svg2 ...]  -> render the viewBox crop of each svg, appended side by side"""
import re, subprocess, sys, os, tempfile
out = sys.argv[1]
x0, y0, x1, y1, s = map(float, sys.argv[3:8])
svgs = [sys.argv[2]] + sys.argv[8:]
outs = []
for i, src in enumerate(svgs):
    t = open(src).read()
    w, h = (x1 - x0) * s, (y1 - y0) * s
    t = re.sub(r'<svg([^>]*?)width="750" height="1050" viewBox="0 0 750 1050"',
               lambda m: f'<svg{m.group(1)}width="{w:.0f}" height="{h:.0f}" viewBox="{x0} {y0} {x1-x0} {y1-y0}"', t, count=1)
    fd, p = tempfile.mkstemp(suffix=".svg", dir="/tmp/claude-1000/-home-luke-Projects-design/55d08c26-3490-4d22-8bb1-5d547fef47ba/scratchpad"); os.close(fd)
    open(p, "w").write(t)
    o = p[:-4] + ".png"
    subprocess.run(["rsvg-convert", p, "-o", o], check=True)
    outs.append(o); os.remove(p)
if len(outs) == 1:
    import shutil; shutil.move(outs[0], out)
else:
    subprocess.run(["magick", *outs, "-background", "#ff00ff", "-splice", "4x0", "+append", out], check=True)
    for o in outs: os.remove(o)
print(out)
