#!/bin/bash
# crop.sh SVG x0 y0 x1 y1 zoom out
svg=$1; x0=$2; y0=$3; x1=$4; y1=$5; z=$6; out=$7
W=$(python3 -c "print(int(750*$z))")
tmp=/tmp/claude-1000/-home-luke-Projects-design/55d08c26-3490-4d22-8bb1-5d547fef47ba/scratchpad/full_$z_$$.png
rsvg-convert -w $W "$svg" -o $tmp
python3 - "$tmp" $x0 $y0 $x1 $y1 $z "$out" <<'PY'
import sys,subprocess
t,x0,y0,x1,y1,z,out=sys.argv[1:]
x0,y0,x1,y1,z=map(float,(x0,y0,x1,y1,z))
g=f"{int((x1-x0)*z)}x{int((y1-y0)*z)}+{int(x0*z)}+{int(y0*z)}"
subprocess.run(["magick",t,"-crop",g,"+repage",out],check=True)
PY
rm -f $tmp
