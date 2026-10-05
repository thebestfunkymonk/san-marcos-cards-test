"""Sandboxed QA harness (review only): builds into build/review/specA/sb and
runs deck.qa.check_piece on arbitrary SVGs without touching cards/ or build/qa."""
import os, sys, json, copy
ROOT='/home/luke/Projects/design/san-marcos-deck'
sys.path.insert(0, ROOT)
os.chdir(ROOT)
SB=os.path.join(ROOT,'build/review/specA/sb')
from deck import build as B, qa as Q
B.ROOT = SB
Q.QA_DIR = os.path.join(SB,'qa')

def build(pid, stock='limestone'):
    return B.build_piece(pid, stock)

def check(info, info_white):
    r = Q.check_piece((info, info_white))
    r.pop('_index_region', None)
    return r

def row(r, keys=None):
    keys = keys or [k for k,_ in Q.COLS]
    out=[]
    for k in keys:
        v=r.get(k)
        out.append(f"{k}:{Q._sym(v)}")
    s=' '.join(out)
    if 'error' in r: s+=' ERROR '+r['error'].splitlines()[-1]
    return s

def details(r, keys):
    return {k: (r.get(k) or {}).get('detail') for k in keys}
