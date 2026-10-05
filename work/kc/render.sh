#!/bin/bash
# usage: work/kc/render.sh <pass> [module]  -> renders KC into work/kc/<pass> + crops
set -e
cd /home/luke/Projects/design/san-marcos-deck
P=${1:?pass}; M=${2:-art/KC.py}
OUT=work/kc/$P; mkdir -p $OUT
.venv/bin/python tools/preview.py $M KC $OUT --qa 2>&1 | grep -v "^\s*$" | tail -20
rsvg-convert -w 2250 $OUT/KC.svg -o $OUT/k3.png
magick $OUT/k3.png -crop 600x660+825+180 +repage $OUT/face.png
magick $OUT/k3.png -crop 720x420+765+150 +repage $OUT/crown.png
magick $OUT/k3.png -crop 420x560+1400+150 +repage $OUT/bird.png
magick $OUT/k3.png -crop 900x700+600+950 +repage $OUT/chest.png
magick $OUT/k3.png -crop 540x540+1350+1050 +repage $OUT/fist.png
magick $OUT/KC-1500.png -crop 1000x1000+270+110 +repage $OUT/top.png
