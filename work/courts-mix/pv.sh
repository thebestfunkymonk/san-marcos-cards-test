#!/bin/bash
# pv.sh <ID> <outdir> [--qa] : preview art/<ID>.py + 3x + crops
id=$1; out=$2; shift 2
cd /home/luke/Projects/design/san-marcos-deck
.venv/bin/python tools/preview.py art/$id.py $id $out "$@" 2>&1 | grep -v "^\[preview\]" | grep -v " ✓ $" 
rsvg-convert -w 2250 $out/$id.svg -o $out/$id-3x.png
magick $out/$id-1500.png -crop 960x940+270+100 +repage $out/$id-top.png
