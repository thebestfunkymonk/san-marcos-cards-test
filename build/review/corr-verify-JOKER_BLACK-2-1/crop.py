import sys, re, subprocess
src, x0, y0, w, h, scale, out = sys.argv[1], *map(float, sys.argv[2:7]), sys.argv[7]
t = open(src).read()
t = re.sub(r'viewBox="[^"]*"', f'viewBox="{x0} {y0} {w} {h}"', t, count=1)
t = re.sub(r'width="750" height="1050"', f'width="{w*scale:.0f}" height="{h*scale:.0f}"', t, count=1)
subprocess.run(['rsvg-convert', '-o', out], input=t.encode(), check=True)
