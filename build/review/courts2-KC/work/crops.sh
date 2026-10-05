#!/bin/bash
# usage: crops.sh <svg> <outprefix> [scale]  -- renders at scale and crops standard KC regions
SVG=$1; OUT=$2; S=${3:-3}
W=$((750*S))
rsvg-convert -w $W "$SVG" -o ${OUT}_full${S}x.png
crop() { # name x0 y0 x1 y1 (card px)
  local n=$1; local x0=$2; local y0=$3; local x1=$4; local y1=$5
  magick ${OUT}_full${S}x.png -crop $(( (x1-x0)*S ))x$(( (y1-y0)*S ))+$((x0*S))+$((y0*S)) +repage ${OUT}_${n}.png
}
crop handL 220 355 360 505
crop handR 460 360 590 480
crop face 310 150 440 290
crop top 139 55 611 511
