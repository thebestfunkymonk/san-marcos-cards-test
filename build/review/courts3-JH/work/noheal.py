# render the top-half composition without heal to an SVG (card coords), for debugging
import sys, os
sys.path.insert(0, '.')
root = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].endswith('.svg') else '.'
sys.path.insert(0, root)
import importlib
m = importlib.import_module('art.JH')
from deck import courtkit as K
sc = m.figure()
res = sc.compose(heal_gaps=False)
out = sys.argv[-1]
L = res.layers()
body = "".join(L[k] for k in L)
open(out, 'w').write(f'<svg xmlns="http://www.w3.org/2000/svg" width="750" height="1050" viewBox="0 0 750 1050"><rect width="750" height="1050" fill="#F4EFE3"/>{body}</svg>')
