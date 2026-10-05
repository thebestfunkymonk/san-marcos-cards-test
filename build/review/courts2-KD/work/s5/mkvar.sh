#!/bin/bash
# mkvar.sh NAME 'python overrides'  -> preview into s5/var/NAME
cd /home/luke/Projects/design/san-marcos-deck
V=build/review/courts2-KD/work/s5/var/$1
mkdir -p $V
cat > $V/mod.py <<PY
import sys; sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
import importlib
import art.KD as M
$2
build = M.build
figure = M.figure
PY
.venv/bin/python tools/preview.py $V/mod.py KD $V --qa > $V/qa.txt 2>&1
tail -25 $V/qa.txt | grep -v "^\s*$" | head -30
