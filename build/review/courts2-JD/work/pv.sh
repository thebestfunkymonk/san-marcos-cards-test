#!/bin/bash
# pv.sh <module.py> <tag>  -> out/<tag>/{JD.png,JD-188.png,JD-1500.png,hL.png,hR.png}
cd /home/luke/Projects/design/san-marcos-deck
W=build/review/courts2-JD/work
O=$W/out/$2; mkdir -p $O
.venv/bin/python tools/preview.py $1 JD $O ${3:---qa} > $O/pv.log 2>&1 || { tail -30 $O/pv.log; exit 1; }
svg=$O/JD.svg
$W/zoom.sh $svg 410 340 110 110 6 $O/hR.png g
$W/zoom.sh $svg 215 415 110 100 6 $O/hL.png g
grep -E "✗|!|FAIL|WARN|balance|fail|warn" $O/pv.log | head -20
