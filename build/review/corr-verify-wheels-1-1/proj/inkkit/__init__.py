"""inkkit — premium vector line-art toolkit (engraving, filigree, guilloche,
monoline Americana, playing-card structure).

Modules: svg (builder, layered Doc, separations), geom (paths, booleans,
knockouts, interlace, curve fitting), stroke (tapered strokes + line styles),
hatch (hatching, half-hatching, tonal engraving), ornament (scrollwork,
guilloche, borders, botanical, radiance, patterns), suits (pips, indices,
layouts, court frames), heraldry (tinctures, shields, crowns), typeset
(alias: type), card (composition, rendering), preflight (print checks),
tokens.
"""
import os as _os
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
FONTS = _os.path.join(ROOT, "fonts")
