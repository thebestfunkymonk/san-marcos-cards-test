#!/bin/bash
# preview JH and make crops
cd /home/luke/Projects/design/san-marcos-deck
.venv/bin/python tools/preview.py art/JH.py JH work/jh/out $@ 2>&1 | grep -v '^\[preview\] JH: status=art' | tail -40
magick work/jh/out/JH-1500.png -crop 960x960+270+110 +repage work/jh/out/top.png
