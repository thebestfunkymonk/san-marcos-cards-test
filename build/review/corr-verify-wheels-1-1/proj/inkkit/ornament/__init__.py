"""Ornament generators. Everything is re-exported here:

    from inkkit import ornament as orn
    orn.filigree_corner(160, 3, x=40, y=40, style="monoline", lw=2.1)
    orn.rosette(375, 525, 60, 120, lobes=24, lines=18, auto_lines=True)
    orn.frame_strip(40, 40, 670, 970, "band", 14, fill="triangles")

Submodules: scrollwork (volutes, scroll(), branch(), acanthus, filigree),
guilloche (spirographs, rosettes, bands, lattices, density control), borders
(frames, strips, frame_strip, cartouches, ribbon), botanical (leaves, sprays,
bluebonnet, wild rice, ripples), radiance (sunbursts, stars, fleurons),
patterns (garment fills).
"""
from .scrollwork import *    # noqa: F401,F403
from .guilloche import *     # noqa: F401,F403
from .borders import *       # noqa: F401,F403
from .botanical import *     # noqa: F401,F403
from .radiance import *      # noqa: F401,F403
from .patterns import *      # noqa: F401,F403
from . import scrollwork, guilloche, borders, botanical, radiance, patterns  # noqa: F401,E402
