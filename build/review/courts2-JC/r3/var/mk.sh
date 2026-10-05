#!/bin/bash
# mk.sh <name> "<python patch lines>"  → $V/<name>/ + crops
set -e
cd /home/luke/Projects/design/san-marcos-deck
V=build/review/courts2-JC/r3/var
n=$1; mkdir -p $V/$n
cat > $V/$n/mod.py <<PY
import sys
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/art")
import JC
$2
build = JC.build
PY
.venv/bin/python tools/preview.py $V/$n/mod.py JC $V/$n ${QA:+--qa} --no-white > $V/$n/log.txt 2>&1 || { tail -20 $V/$n/log.txt; exit 1; }
svg=$(ls $V/$n/*.svg | head -1)
rsvg-convert -w 2250 $svg -o $V/$n/x3.png
magick $V/$n/x3.png -crop 450x420+600+1140 +repage $V/$n/hL3.png; magick $V/$n/x3.png -crop 420x420+1350+960 +repage $V/$n/hR3.png; magick $V/$n/JC.png -crop 200x200+400+300 +repage -resize 200% $V/$n/hR750.png
magick $V/$n/x3.png -crop 150x150+765+1290 +repage -filter point -resize 300% $V/$n/j9.png
