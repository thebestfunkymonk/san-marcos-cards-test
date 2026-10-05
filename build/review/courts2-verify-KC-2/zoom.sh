#!/bin/bash
# zoom.sh SVG x y w h scale out
SVG=$1; X=$2; Y=$3; W=$4; H=$5; S=$6; OUT=$7
python3 - "$SVG" "$X" "$Y" "$W" "$H" "$S" "$OUT" <<'PY'
import sys,re,subprocess
svg,x,y,w,h,s,out=sys.argv[1:]
x,y,w,h,s=map(float,(x,y,w,h,s))
src=open(svg).read()
m=re.search(r'<svg[^>]*>',src)
head=m.group(0)
vb=re.search(r'viewBox="([^"]+)"',head).group(1).split()
W0=float(re.search(r'\swidth="([\d.]+)',head).group(1)) if re.search(r'\swidth="([\d.]+)',head) else float(vb[2])
# card px coords assume viewBox units == card px at 750 width
k=float(vb[2])/750.0
nh=re.sub(r'viewBox="[^"]+"',f'viewBox="{float(vb[0])+x*k} {float(vb[1])+y*k} {w*k} {h*k}"',head)
nh=re.sub(r'\swidth="[^"]+"',f' width="{w*s}"',nh)
nh=re.sub(r'\sheight="[^"]+"',f' height="{h*s}"',nh)
open('/home/luke/Projects/design/san-marcos-deck/build/review/courts2-verify-KC-2/_z.svg','w').write(src.replace(head,nh,1))
subprocess.run(['rsvg-convert','/home/luke/Projects/design/san-marcos-deck/build/review/courts2-verify-KC-2/_z.svg','-o',out],check=True)
PY
