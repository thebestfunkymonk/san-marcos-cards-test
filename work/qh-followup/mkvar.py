"""make a variant of art/QH.py with overridden AIR / AIR_SIZES / call"""
import sys, re
name, air, sizes, call = sys.argv[1:5]
s = open('art/QH.py').read()
s = re.sub(r'^AIR = .*$', 'AIR = ' + air, s, flags=re.M)
s = re.sub(r'^AIR_SIZES = .*$', 'AIR_SIZES = ' + sizes, s, flags=re.M)
s = re.sub(r'A\.bubble_ribbon\(AIR, AIR_SIZES[^\n]*\), None, sil=False\)', call + ', None, sil=False)', s)
open(f'work/qh-followup/QH_{name}.py', 'w').write(s)
