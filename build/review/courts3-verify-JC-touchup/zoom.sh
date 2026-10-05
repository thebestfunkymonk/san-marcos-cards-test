#!/bin/bash
# zoom.sh in.svg x y w h scale out.png   (card coords)
in=$1; x=$2; y=$3; w=$4; h=$5; s=$6; out=$7
W=$(python3 -c "print(int($w*$s))"); H=$(python3 -c "print(int($h*$s))")
sed -e "0,/viewBox=\"0 0 750 1050\"/s//viewBox=\"$x $y $w $h\"/" -e "0,/width=\"750\" height=\"1050\"/s//width=\"$W\" height=\"$H\"/" "$in" > /tmp/claude-1000/-home-luke-Projects-design/55d08c26-3490-4d22-8bb1-5d547fef47ba/scratchpad/zoom_$$.svg
rsvg-convert /tmp/claude-1000/-home-luke-Projects-design/55d08c26-3490-4d22-8bb1-5d547fef47ba/scratchpad/zoom_$$.svg -o "$out"; rm /tmp/claude-1000/-home-luke-Projects-design/55d08c26-3490-4d22-8bb1-5d547fef47ba/scratchpad/zoom_$$.svg
