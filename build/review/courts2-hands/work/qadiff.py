import json, sys
b = {p['id']: p for p in json.load(open(sys.argv[1]))['pieces']}
a = {p['id']: p for p in json.load(open(sys.argv[2]))['pieces']}
def regs(p):
    out = []
    r = p['12'].get('raster', {}) or {}
    for lay, d in r.items():
        for kind in ('thin', 'gaps'):
            for g in d.get(kind, []):
                bb = g['bbox']
                if bb[1] < 525:  # top half only (the bottom is the 180° copy)
                    out.append((lay, kind, tuple(round(x) for x in bb)))
    return out
for pid in a:
    rb, ra = set(regs(b[pid])), set(regs(a[pid]))
    new = sorted(ra - rb); gone = sorted(rb - ra)
    vb, va = b[pid]['12'].get('vector', []), a[pid]['12'].get('vector', [])
    print(pid, 'vector', len(vb), '->', len(va), '| raster', len(rb), '->', len(ra))
    for x in new: print('   + ', x)
    for x in gone: print('   - ', x)
