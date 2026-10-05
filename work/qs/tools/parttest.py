"""Render isolated parts: import this and call show(parts, out, box, scale)."""
import sys
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/work/qs/tools")
from r import render, montage
from deck import courtkit as K
from deck.motifs import core as C


def scene_of(parts, rank=None, contour=True):
    sc = K.Scene(rank=rank)
    for i, p in enumerate(parts):
        if isinstance(p, tuple):
            nm, pt, kw = p
            sc.part(nm, pt, **kw)
        else:
            sc.part(f"p{i}", p)
    return sc


def show(parts, out, box, scale=3.0, contour=True, heal=True):
    sc = scene_of(parts)
    f = sc.compose(contour=K.CONTOUR if contour else 0, heal_gaps=heal)
    render(f, out, box, scale)
    return sc
