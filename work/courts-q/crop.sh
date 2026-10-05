#!/bin/bash
# crop.sh <svg> <cx> <cy> <half> <scale> <out>
svg=$1; cx=$2; cy=$3; h=$4; s=$5; out=$6
w=$(python3 -c "print(int(750*$s))")
tmp=/tmp/claude-1000/-home-luke-Projects-design/55d08c26-3490-4d22-8bb1-5d547fef47ba/scratchpad/full_$(echo "$(realpath $svg)" | md5sum | cut -c1-10)_$s.png
if [ ! -f $tmp ] || [ $svg -nt $tmp ]; then rsvg-convert -w $w $svg -o $tmp; fi
x0=$(python3 -c "print(int(($cx-$h)*$s))"); y0=$(python3 -c "print(int(($cy-$h)*$s))"); sz=$(python3 -c "print(int(2*$h*$s))")
magick $tmp -crop ${sz}x${sz}+${x0}+${y0} +repage $out
