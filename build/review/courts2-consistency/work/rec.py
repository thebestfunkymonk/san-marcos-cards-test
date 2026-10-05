import sys, json, os
sys.path.insert(0, os.getcwd()); sys.path.insert(0, os.path.join(os.getcwd(), "tools"))
import hand_specimen as H
import numpy as np
calls = H.record(H.COURTS)
def conv(o):
    if isinstance(o, (np.ndarray,)): return o.tolist()
    if isinstance(o, (np.floating,)): return float(o)
    if isinstance(o, tuple): return list(o)
    return str(o)
out=[]
for c in calls:
    out.append({"id":c["id"],"fn":c["fn"],"args":c["args"],"kw":{k:v for k,v in c["kw"].items()}})
json.dump(out, open(sys.argv[1],"w"), default=conv, indent=1)
for c in out:
    a=c["args"]; kw=c["kw"]
    print(c["id"], c["fn"], json.dumps(a, default=conv), {k:(json.loads(json.dumps(v,default=conv))) for k,v in kw.items() if k in ("wrist","back","hand","side","h","length","width","wrist_w","shaft_w")})
