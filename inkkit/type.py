"""Alias of :mod:`inkkit.typeset` (named ``type`` in the spec). Prefer
``from inkkit.typeset import text_to_path`` to avoid shadowing the builtin."""
from .typeset import *  # noqa: F401,F403
from .typeset import __all__  # noqa: F401
