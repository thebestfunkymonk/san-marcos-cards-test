import sys, hashlib, json
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
from deck import build as B
pid = sys.argv[1]
h = []
for _ in range(2):
    mod = B.load_art(pid)
    h.append(hashlib.md5(json.dumps(mod.build(), sort_keys=True).encode()).hexdigest())
print(pid, h[0] == h[1], h)
