import sys, os
sys.path.insert(0,'/home/luke/Projects/design/san-marcos-deck/build/review/specA')
from harness import *
SBP='/home/luke/Projects/design/san-marcos-deck/build/review/specA/sb'
sys.path.insert(0, SBP); sys.modules.pop('art', None)
ids = B.GROUPS['numbers'] + ['KS','QS','JS','KH','KC','QC','JC','KD','QD','JD'] + ['AS','AH','AC','AD']
# aces: sandbox art dir has no ace modules -> placeholders (system pip + keyline)
code = Q.main(ids)
print('EXIT', code)
