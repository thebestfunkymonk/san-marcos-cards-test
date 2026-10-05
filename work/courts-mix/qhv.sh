#!/bin/bash
# qhv.sh <outdir> '<json overrides>'
cd /home/luke/Projects/design/san-marcos-deck
QHV="$2" .venv/bin/python tools/preview.py work/courts-mix/qh_try.py QH $1 --no-white 2>&1 | grep -v "^\[preview\]"
rsvg-convert -w 2250 $1/QH.svg -o $1/QH-3x.png
magick $1/QH-3x.png -crop 600x600+840+270 +repage $1/cap3.png
