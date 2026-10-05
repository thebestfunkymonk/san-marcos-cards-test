"""art/_kc_hair.py — the K♣'s hair falls, refined locally on top of deck.courtkit.

``hair_fall_clear``: the kit's ``hair_fall`` keeping only the first ``keep``
current lines. Beside the K♣'s frontal egg the visible band of each lock (the
fan's outer edge to the face, and lower down to the beard) is ≈ 16 px wide:
room for ONE current line with §I.12's paper either side. The kit's second
line (7 px further in) runs within 0–3 px of the face edge from the crown to
the chin — heal trimmed the head outline at the temples to make room for it
(the paper face met the gold with no edge from the crown to the eye line) and
left 1–2 px gold wedges and stubs beside the face and the beard. With the one
line kept and the fan set 2 px further out (``KC.HAIR``), line 0 clears the
face and the beard outlines by ≥ 4.2 px everywhere and the head outline runs
unbroken from the crown band to the beard.
"""
from __future__ import annotations

from deck import courtkit as K
from deck.motifs import core as C


def hair_fall_clear(fc, side, spec: K.HairSpec, keep=1) -> K.Part:
    part = K.hair_fall(fc, side, spec)
    out, n = [], 0
    for m in part.lines.marks:
        role = m.role.split("@")[0]
        if role == "current":
            n += 1
        if role in ("current", "terminal") and n > keep:
            continue
        out.append(m)
    return K.Part(part.shape, part.fills, C.Frag(out, part.lines.meta), part.meta)
