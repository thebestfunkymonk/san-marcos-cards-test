#!/bin/bash
# before/after montage: rows = courts, cols = L before, L after, R before, R after (3x crops, labelled)
out=$1; shift
ids=${@:-KS QS JS KH QH JH KC QC JC KD QD JD}
FONT=/usr/share/fonts/noto/NotoSans-Regular.ttf
args=()
for i in $ids; do
  args+=(-label "$i L before" before/${i}_L.png -label "$i L after" after/${i}_L.png -label "$i R before" before/${i}_R.png -label "$i R after" after/${i}_R.png)
done
magick montage -font $FONT -pointsize 16 "${args[@]}" -tile 4x -geometry 390x390+5+5 -background '#8a8a8a' $out
