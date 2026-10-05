#!/bin/bash
# preview JS into work/js/pv/<tag> and make crops: top half at 1x, face 3x, lantern 3x, coil 3x
cd /home/luke/Projects/design/san-marcos-deck
TAG=${1:-cur}; shift
OUT=work/js/pv/$TAG
mkdir -p $OUT
.venv/bin/python tools/preview.py art/JS.py JS $OUT "$@" 2>&1 | grep -v 'status=art' | tail -45
rsvg-convert -w 2250 $OUT/JS.svg -o $OUT/JS-3x.png
magick $OUT/JS-1500.png -crop 960x940+270+100 +repage $OUT/top.png
magick $OUT/JS-3x.png -crop 600x600+870+330 +repage $OUT/face.png
magick $OUT/JS-3x.png -crop 540x780+1360+600 +repage $OUT/lantern.png
magick $OUT/JS-3x.png -crop 720x660+420+960 +repage $OUT/coil.png
