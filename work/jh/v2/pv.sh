#!/bin/bash
# preview JH (art/JH.py) → work/jh/v2/out, + crops: top half 2x, face 3x, 188
cd /home/luke/Projects/design/san-marcos-deck
O=work/jh/v2/out
mkdir -p $O
.venv/bin/python tools/preview.py art/JH.py JH $O "$@" 2>&1 | grep -v '^\[preview\] JH: status=art' | tail -30
magick $O/JH-1500.png -crop 960x960+270+110 +repage $O/top.png
rsvg-convert -w 2250 $O/JH.svg -o $O/JH-3x.png
magick $O/JH-3x.png -crop 540x600+870+330 +repage $O/face.png
