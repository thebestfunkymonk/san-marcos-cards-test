import sys, os; sys.path.insert(0,'/home/luke/Projects/design/san-marcos-deck/build/review/specA')
from harness import *
a=dict(B.parse('BACK')); a.update(status='art', svg=os.path.join(SB,'cards/BACK.svg'), order=list(T.LAYERS) if False else None)
