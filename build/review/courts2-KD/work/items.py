import sys, warnings; sys.path.insert(0,'.'); warnings.simplefilter('ignore')
import importlib.util
spec = importlib.util.spec_from_file_location('kdi', sys.argv[1]); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
sc = m.figure()
for it in sc.items:
    b = tuple(round(v,1) for v in it.occ.bounds) if it.occ is not None and not it.occ.is_empty else None
    print(f"{it.name:22s} sil={it.sil!s:5s} halo={it.halo} bounds={b} marks={len(it.frag.marks)} roles={sorted({mk.role for mk in it.frag.marks})[:8]}")
