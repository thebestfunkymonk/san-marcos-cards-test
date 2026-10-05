#!/bin/bash
# preview JH (art/JH.py) -> work/jh/v3/out (+ 3x and crops)
cd /home/luke/Projects/design/san-marcos-deck
O=work/jh/v3/out
mkdir -p $O
.venv/bin/python tools/preview.py art/JH.py JH $O "$@" 2>&1 | grep -v '^\[preview\] JH: status=art' | tail -30
magick $O/JH-1500.png -crop 960x960+270+110 +repage $O/top.png
rsvg-convert -w 2250 $O/JH.svg -o $O/JH-3x.png
I=$O/JH-3x.png
magick $I -crop 600x600+930+180 +repage $O/c_head.png
magick $I -crop 540x600+870+330 +repage $O/c_face.png
magick $I -crop 420x540+630+1080 +repage $O/c_bowhand.png
magick $I -crop 480x600+1350+400 +repage $O/c_fidtop.png
magick $I -crop 480x660+1350+860 +repage $O/c_fidbody.png
magick $I -crop 600x660+780+840 +repage $O/c_chest.png
