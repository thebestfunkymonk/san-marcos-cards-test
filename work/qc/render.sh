#!/bin/bash
# render a draft of art/QC.py into work/qc/out/<tag>: 750, 188, 1500, white + 3x crops
cd /home/luke/Projects/design/san-marcos-deck
tag=${1:-p}
out=work/qc/out/$tag
mkdir -p $out
.venv/bin/python tools/preview.py art/QC.py QC $out ${QA:+--qa} 2>&1 | tail -40
rsvg-convert -w 2250 $out/QC.svg -o $out/QC-3x.png
magick $out/QC-3x.png -crop 480x480+915+360 +repage $out/face3x.png
magick $out/QC-3x.png -crop 1500x1400+417+165 +repage -resize 50% $out/top.png
magick $out/QC-1500.png -crop 960x960+270+100 +repage $out/top1500.png
