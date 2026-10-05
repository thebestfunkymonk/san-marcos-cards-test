#!/bin/bash
# zoom.sh ID x0 y0 x1 y1 out [scale]  — crop a card-px bbox (padded 12) at scale (default 8)
id=$1; x0=$2; y0=$3; x1=$4; y1=$5; out=$6; s=${7:-8}
p=12
w=$(( (x1 - x0 + 2*p) * s )); h=$(( (y1 - y0 + 2*p) * s ))
X=$(( (x0 - p) * s )); Y=$(( (y0 - p) * s ))
rsvg-convert -w $(( 750 * s )) ../../../../cards/$id.svg -o /tmp/claude-1000/-home-luke-Projects-design/55d08c26-3490-4d22-8bb1-5d547fef47ba/scratchpad/zoom_full.png
magick /tmp/claude-1000/-home-luke-Projects-design/55d08c26-3490-4d22-8bb1-5d547fef47ba/scratchpad/zoom_full.png -crop ${w}x${h}+${X}+${Y} +repage $out
