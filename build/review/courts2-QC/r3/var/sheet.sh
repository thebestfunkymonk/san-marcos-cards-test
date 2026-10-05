#!/bin/bash
# sheet.sh OUT x y w h z  names...  : side-by-side crops from var/<name>/QC-1500.png (z<=2) or rsvg at 3x
out=$1; x=$2; y=$3; w=$4; h=$5; z=$6; shift 6
T=/tmp/claude-1000/-home-luke-Projects-design/55d08c26-3490-4d22-8bb1-5d547fef47ba/scratchpad
files=()
for n in "$@"; do
  W=$(python3 -c "print(int(750*$z))")
  rsvg-convert -w $W $n/QC.svg -o $T/sh_$n.png
  g=$(python3 -c "print(f'{int($w*$z)}x{int($h*$z)}+{int($x*$z)}+{int($y*$z)}')")
  magick $T/sh_$n.png -crop $g +repage -gravity north -background white -splice 0x14 -pointsize 12 -annotate +0+0 "$n" $T/shc_$n.png
  files+=($T/shc_$n.png)
done
magick "${files[@]}" -bordercolor magenta -border 2 +append $out
