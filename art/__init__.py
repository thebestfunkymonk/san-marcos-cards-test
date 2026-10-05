"""HEADWATERS art modules: one module per piece, ``art/<ID>.py``, exposing
``build() -> {layer: [svg fragments]}`` in card coordinates.

See art/README.md and deck/ART_CONTRACT.md for the contract. The deck
builder (``python -m deck.build``) imports these; missing pieces build as
placeholders.
"""
from __future__ import annotations

import importlib
import os

PIECES = (["KS", "QS", "JS", "KH", "QH", "JH", "KC", "QC", "JC", "KD", "QD", "JD"] +
          ["AS", "AH", "AC", "AD", "JOKER_RED", "JOKER_BLACK", "BACK"])
_HERE = os.path.dirname(os.path.abspath(__file__))


def available() -> list[str]:
    """Piece IDs that currently have an art module."""
    return [p for p in PIECES if os.path.isfile(os.path.join(_HERE, f"{p}.py"))]


def load(pid: str):
    """Import ``art/<pid>.py`` (reloaded), or None if it does not exist."""
    if not os.path.isfile(os.path.join(_HERE, f"{pid}.py")):
        return None
    mod = importlib.import_module(f"{__name__}.{pid}")
    return importlib.reload(mod)
