#!/bin/bash
# usage: pv.sh <module.py> <outdir>   (run from anywhere)
set -e
R=/home/luke/Projects/design/san-marcos-deck
cd $R
M=${1:-work/kh/tools/fast.py}; O=${2:-work/kh/cur}
mkdir -p $O
.venv/bin/python tools/preview.py $M KH $O --no-white 2>&1 | grep -v '^\[preview\] KH: status=art' || true
.venv/bin/python work/kh/tools/bal.py $O/KH.svg
rsvg-convert -w 2250 $O/KH.svg -o $O/k3.png
magick $O/k3.png -crop 600x660+825+220 +repage $O/face3.png
magick $O/k3.png -crop 1440x1380+405+150 +repage -resize 50% $O/top.png
magick $O/k3.png -crop 540x540+540+1000 +repage $O/handL3.png
magick $O/k3.png -crop 540x540+1350+1000 +repage $O/handR3.png
magick $O/k3.png -crop 480x420+885+1080 +repage $O/win3.png
