#!/bin/bash
# usage: rv.sh <outdir> [module]   full preview (healed) + crops + balance
set -e
R=/home/luke/Projects/design/san-marcos-deck
cd $R
O=${1:-work/kh/cur}; M=${2:-art/KH.py}
mkdir -p $O
.venv/bin/python tools/preview.py $M KH $O --no-white 2>&1 | grep -v 'status=art' || true
.venv/bin/python work/kh/tools/bal.py $O/KH.svg
rsvg-convert -w 2250 $O/KH.svg -o $O/k3.png
magick $O/KH-1500.png -crop 960x940+270+100 +repage $O/top.png
magick $O/k3.png -crop 600x660+825+220 +repage $O/face3.png
magick $O/k3.png -crop 660x420+780+150 +repage $O/crown3.png
magick $O/k3.png -crop 480x330+885+1110 +repage $O/win3.png
magick $O/k3.png -crop 540x600+540+780 +repage $O/handL3.png
magick $O/k3.png -crop 480x480+1320+1000 +repage $O/handR3.png
