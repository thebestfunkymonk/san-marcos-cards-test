import re, inspect, sys
sys.path.insert(0, "../../..")
import deck.motifs as DM
from deck.motifs import forms
txt = open("../../../deck/motifs/README.md").read()
# table rows: | § | `name(args)` | ...  or | `name(args)` | ...
sigs = re.findall(r"`([a-z_][a-z0-9_]*)\(([^`]*)\)`", txt)
seen = set()
for name, args in sigs:
    if name in seen: continue
    fn = getattr(DM, name, None) or getattr(forms, name, None)
    if fn is None or not callable(fn): continue
    try: sp = inspect.signature(fn)
    except Exception: continue
    for part in re.split(r",\s*(?![^()]*\))", args):
        m = re.match(r"\s*([a-z_0-9]+)\s*=\s*(.+)$", part)
        if not m: continue
        k, v = m.group(1), m.group(2).strip()
        if k not in sp.parameters:
            print(f"{name}: README param '{k}' not in signature"); continue
        d = sp.parameters[k].default
        if d is inspect._empty: continue
        vv = v.replace("w", "") if False else v
        try:
            ev = eval(v, {"T": __import__("deck.tokens", fromlist=["x"]), "None": None, "True": True, "False": False})
        except Exception:
            continue
        if isinstance(ev, (int, float)) and isinstance(d, (int, float)) and abs(float(ev) - float(d)) > 1e-9:
            print(f"{name}: README {k}={v} but code default {k}={d!r}")
        elif isinstance(ev, tuple) and tuple(ev) != tuple(d if isinstance(d, tuple) else (d,)):
            print(f"{name}: README {k}={v} but code default {k}={d!r}")
    seen.add(name)
