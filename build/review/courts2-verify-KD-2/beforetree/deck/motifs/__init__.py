"""HEADWATERS ornament library (Track B) — see deck/motifs/README.md.

    from deck.motifs import *            # core helpers + geometric + figurative motifs
    from deck.motifs import core as C, geometric as M

Every motif is generated at FINAL size and returns a ``Frag``: per-layer SVG
fragments for line-on-ground drawing (``frag.layers()``) and the exact union
of its marks for geometric knockouts (``knockout(solid, frag)``).
"""
from .core import *  # noqa: F401,F403
from .core import __all__ as _core_all
from .geometric import *  # noqa: F401,F403
from .geometric import __all__ as _geo_all
# Track B2 figurative motifs (forms stays a module: deck.motifs.forms)
from . import forms  # noqa: F401
from .lion import *  # noqa: F401,F403
from .lion import __all__ as _lion_all
from .rice import *  # noqa: F401,F403
from .rice import __all__ as _rice_all
from .fauna import *  # noqa: F401,F403
from .fauna import __all__ as _fauna_all
from .hair import *  # noqa: F401,F403
from .hair import __all__ as _hair_all

__all__ = (list(_core_all) + list(_geo_all) + list(_lion_all) + list(_rice_all) + list(_fauna_all)
           + list(_hair_all))
