#!/bin/bash
# preview JH into work/jh-final/out/<tag> and make crops: 750, 188, 3x face, 3x pegs
cd /home/luke/Projects/design/san-marcos-deck
TAG=${1:-cur}; shift
O=work/jh-final/out/$TAG
.venv/bin/python tools/preview.py art/JH.py JH $O "$@" 2>&1 | grep -v 'status=art' | tail -40
rsvg-convert -w 2250 $O/JH.svg -o $O/JH-3x.png
magick $O/JH-3x.png -crop 600x600+900+400 +repage $O/face3x.png
magick $O/JH-3x.png -crop 330x480+1430+380 +repage $O/pegs3x.png
magick $O/JH-3x.png -crop 300x300+960+660 +repage $O/jaw3x.png
