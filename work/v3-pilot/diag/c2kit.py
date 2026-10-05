"""work/v3-pilot/diag/c2kit.py — whole-card C2 composition for continuous double-head courts.

The idea (ART_CONTRACT §3.1b): the system clips the top half's art along the
seam and adds its 180° copy. If the art we hand it is ALREADY exactly C2
(equal to its own 180° rotation about (375, 525)), the card the system
prints is that art, unchanged, whatever the seam: the seam is invisible by
construction, no matter what crosses it.

So a court is composed as the WHOLE card: every part that is not C2 by
construction goes into the Scene as ONE item ``part ∪ rot180(part)``
(painter's order is then C2-consistent: A behind rot(B) ⇔ rot(A) behind B),
garments that run through the centre are built as C2 shapes once, and the
composed result is clipped to the art window (itself C2) and healed once.

    sc = C2Scene()
    sc.part("mantle", mantle_part, c2=False)   # already C2
    sc.part("head", head_part)                 # doubled here
    layers = sc.layers()
"""
from __future__ import annotations

import shapely
import shapely.affinity

from deck import courtkit as K
from deck import frames as F
from deck import tokens as T

CX, CY = float(T.CX), float(T.CY)


def rot(g):
    """180° about the card centre: shapely geometry, d string (→ shapely) or point."""
    if isinstance(g, str):
        g = K.R(g)
    if isinstance(g, (tuple, list)) or hasattr(g, "shape") and getattr(g, "shape", None) == (2,):
        return K.P(2 * CX - g[0], 2 * CY - g[1])
    return shapely.affinity.rotate(g, 180.0, origin=(CX, CY))


def c2_region(g):
    g = K.R(g)
    return K.U(g, rot(g))


def c2_part(p: K.Part) -> K.Part:
    """p ∪ its 180° copy, as one Part (shape, fills, lines doubled)."""
    return K.Part(K.U(p.shape, rot(p.shape)), p.fills + p.fills.rot180(), p.lines + p.lines.rot180(), dict(p.meta))


def is_c2(g, tol=0.5) -> bool:
    g = K.R(g)
    return g.symmetric_difference(rot(g)).area < tol * max(1.0, g.length)


class C2Scene(K.Scene):
    """A K.Scene (rank=None: no band clip) whose ``part``/``add`` double
    every item with its 180° copy unless ``c2=False`` (already C2)."""

    def add(self, name, frag, occ=None, sil=True, halo=0.0, halo_skip=(), halo_only=None, halo_zone=None,
            c2=True):
        if isinstance(frag, K.Part):
            occ = frag.shape if occ is None else occ
            frag = frag.frag
        if c2:
            frag = frag + frag.rot180() if frag is not None else frag
            if occ is not None:
                occ = c2_region(occ)
            if halo_zone is not None:
                halo_zone = c2_region(halo_zone)
        return super().add(name, frag, occ, sil=sil, halo=halo, halo_skip=halo_skip, halo_only=halo_only,
                           halo_zone=halo_zone)

    def part(self, name, part, c2=True, **kw):
        return self.add(name, part.frag, part.shape, c2=c2, **kw)

    def compose_card(self, contour=K.CONTOUR):
        res = K.Scene.compose(self, contour=contour, heal_gaps=False)
        win = K.R(F.art_window_d())
        res = K.clip_in(res, win, self.clip_tol)
        self.heal_log = []
        return K.heal(res, log=self.heal_log)

    def layers(self, **kw):
        return K.layers(self.compose_card(**kw))
