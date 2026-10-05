import sys, os
sys.path.insert(0,'/home/luke/Projects/design/san-marcos-deck/build/review/specA')
from harness import *
SBP='/home/luke/Projects/design/san-marcos-deck/build/review/specA/sb'
sys.path.insert(0, SBP); sys.modules.pop('art', None)
code = Q.main(sys.argv[1:])
print('EXIT CODE', code)
