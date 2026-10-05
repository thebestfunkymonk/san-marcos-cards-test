"""trad_kit: a reusable court-card construction kit for HEADWATERS.

Built for the K♠ "traditional pattern, re-skinned" study and meant to carry
the other 11 courts. Modules:

    shapes   path helpers: smooth/corner runs, bilateral (mirrored) outlines,
             ribbons along guides, shapely <-> d conversion
    scene    painter's-algorithm compositor: back-to-front Items (fill colour,
             contour weights, knockouts, detail lines) -> {layer: svg}
             with occlusion done as geometry (no paper paint)
    face     the §H.0 face kit (frontal / 3/4 / profile-ready parameters)
    locks    §G.24 current lines: hair, beard and moustache locks
    hands    §H.0 mitten hands: fist round a staff, cupping hand
    regalia  crown base + merlons, orb, banded sceptre, rosette jewel, Lion Mark
    garments mantle / collar / tunic pattern fills (strata, karst voids, trims)

All geometry is authored at final size in card px; every stroke uses a
legal §B.2 width via deck.motifs (Frag / stroke / hatch).
"""
