#!/bin/bash
# qhc.sh <outdir> '<json overrides>' : quick QH render + cap crops (no white, no qa)
cd /home/luke/Projects/design/san-marcos-deck
mkdir -p $1
QHV="$2" .venv/bin/python tools/preview.py work/courts-mix/qh_try.py QH $1 --no-white 2>&1 | grep -v "^\[preview\]" | grep -v " ✓ $"
rsvg-convert -w 3000 $1/QH.svg -o $1/QH-4x.png
magick $1/QH-4x.png -crop 760x600+1080+340 +repage $1/cap4.png
magick $1/QH.png -crop 300x260+230+60 +repage -resize 200% $1/cap1x.png
