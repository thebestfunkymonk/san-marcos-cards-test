#!/bin/bash
# zoom.sh <svg> <x> <y> <w> <h> <scale> <out.png> [grid]
svg=$1; x=$2; y=$3; w=$4; h=$5; s=$6; out=$7
tmp=$(mktemp --suffix=.svg)
pw=$(python3 -c "print(int($w*$s))"); ph=$(python3 -c "print(int($h*$s))")
sed -e "0,/<svg [^>]*>/s//<svg xmlns=\"http:\/\/www.w3.org\/2000\/svg\" width=\"$pw\" height=\"$ph\" viewBox=\"$x $y $w $h\">/" "$svg" > "$tmp"
rsvg-convert "$tmp" -o "$out"
rm -f "$tmp"
if [ -n "$8" ]; then
  # draw a 10px grid label ticks
  python3 - "$out" $x $y $w $h $s <<'PY'
import sys
from PIL import Image, ImageDraw
p,x,y,w,h,s=sys.argv[1],*map(float,sys.argv[2:])
im=Image.open(p).convert('RGB'); d=ImageDraw.Draw(im)
import math
for gx in range(int(math.ceil(x/10)*10), int(x+w)+1, 10):
    X=(gx-x)*s; d.line([(X,0),(X,8 if gx%50 else 18)],fill=(255,0,255),width=1)
    if gx%50==0: d.text((X+2,18),str(gx),fill=(255,0,255))
for gy in range(int(math.ceil(y/10)*10), int(y+h)+1, 10):
    Y=(gy-y)*s; d.line([(0,Y),(8 if gy%50 else 18,Y)],fill=(255,0,255),width=1)
    if gy%50==0: d.text((20,Y+2),str(gy),fill=(255,0,255))
im.save(p)
PY
fi
