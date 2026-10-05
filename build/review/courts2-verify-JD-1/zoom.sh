#!/bin/bash
# zoom.sh in.svg x y w h scale out.png
in=$1; x=$2; y=$3; w=$4; h=$5; s=$6; out=$7
tmp=$(mktemp --suffix=.svg -p /tmp/claude-1000/-home-luke-Projects-design/55d08c26-3490-4d22-8bb1-5d547fef47ba/scratchpad)
sed -E "0,/<svg /s#<svg [^>]*>#<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"$(python3 -c "print($w*$s)")\" height=\"$(python3 -c "print($h*$s)")\" viewBox=\"$x $y $w $h\">#" "$in" > $tmp
rsvg-convert $tmp -o $out
rm $tmp
