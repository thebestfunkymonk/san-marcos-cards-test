import sys, os, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'arms.py')).read().split("a0 = QC.SCEPTRE")[0])
best = []
for h0 in (58.0, 62.0, 66.0):
  for p1 in ((18.0, 50.0), (20.0, 50.0)):
    for p2 in ((32.0, 60.0), (30.0, 62.0), (34.0, 58.0), (28.0, 64.0)):
      for p3 in ((12.0, 30.0), (9.0, 30.0), (6.0, 30.0), (12.0, 20.0), (10.0, 36.0)):
        for f0 in (0.30, 0.33, 0.36):
          for f1 in (0.52, 0.56, 0.60):
            for hg1 in (0.0, -8.0, -15.0):
              for tipL in (22.0, 19.0):
                arm = (245.0, h0, (p1, p2, p3), 6.0, ((f0, 7.0, 22.0, 7.6, 0.0), (f1, 7.0, 22.0, 7.6, hg1)), (tipL, 7.6))
                r = evaluate(*arm)
                m = min(r['f0-arm'] - 7.3, r['f1-arm'] - 7.3, r['f0-f1'] - 7.3, r['f1-tip'] - 7.3, r['f0-tip'] - 7.3,
                        r['hair'] - 8.85, r['cloak'] - 8.85)
                # change cost vs the original
                cost = abs(h0 - 62) / 4 + abs(p2[0] - 32) / 4 + abs(p3[0] - 12) / 3 + abs(f1 - 0.61) * 10 + abs(hg1) / 8 + abs(22 - tipL) / 3
                best.append((m, -cost, arm, r))
best.sort(key=lambda z: (z[0] >= 0, z[1] if z[0] >= 0 else z[0]), reverse=True)
for m, c, arm, r in best[:12]:
    print(f'm={m:.2f} cost={-c:.2f}', arm[1], arm[2], [f[0] for f in arm[4]], arm[4][1][4], arm[5][0], ' '.join(f'{k}={v:.1f}' for k, v in r.items()))
