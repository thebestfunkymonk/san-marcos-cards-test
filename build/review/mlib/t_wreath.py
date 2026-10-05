from rh import *
from deck.motifs import rice as RI
from deck.motifs import sheet_figurative as SF
import inspect
src = inspect.getsource(SF.specimens)
import re
print([l.strip() for l in src.splitlines() if 'wreath' in l][:6])
w = RI.rice_wreath_arc(375, 470, 175)
print("default A-club wreath warnings:", len(w.meta.get('warnings',[])), w.meta.get('warnings',[])[:2], "pairs", w.meta['n_pairs'])
show(w, "wreath-ac-default-2x", zoom=2)
show(w, "wreath-ac-default-1x", zoom=1)
