#!/bin/bash
# usage: rv.sh <version>  — full preview + standard crops
cd /home/luke/Projects/design/san-marcos-deck
V=$1; D=work/kd/out/$V; mkdir -p $D
.venv/bin/python tools/preview.py art/KD.py KD $D ${2:---qa} 2>&1 | grep -E '✗|!|error|Error|Traceback' | head -20
rsvg-convert -w 2250 $D/KD.svg -o $D/KD3.png
magick $D/KD3.png -crop 600x660+870+300 +repage $D/face3.png
magick $D/KD-1500.png -crop 960x960+270+100 +repage $D/top2x.png
magick $D/KD3.png -crop 750x600+600+1050 +repage $D/handL3.png
magick $D/KD3.png -crop 600x1400+1350+150 +repage $D/key3.png
[ -f $D/KD-qa.json ] && python3 -c "import json;d=json.load(open('$D/KD-qa.json'));print('balance',d['5']['balance']);print('12',d['12'].get('ok'),str(d['12'].get('detail'))[:600])"
