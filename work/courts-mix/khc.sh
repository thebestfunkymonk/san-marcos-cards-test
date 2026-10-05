#!/bin/bash
# khc.sh <outdir> '<json overrides>' [--qa]: quick KH render + window crops
cd /home/luke/Projects/design/san-marcos-deck
mkdir -p $1
KHV="$2" .venv/bin/python tools/preview.py work/courts-mix/kh_try.py KH $1 --no-white $3 > $1.log 2>&1
rsvg-convert -w 3000 $1/KH.svg -o $1/KH-4x.png
magick $1/KH-4x.png -crop 640x520+1180+1470 +repage $1/win4.png
magick $1/KH.png -crop 170x140+290+362 +repage -resize 300% $1/win1x.png
