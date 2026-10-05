import re, sys
sys.path.insert(0,'.')
from inkkit import geom as G
import shapely
def layer_paths(svgfile):
    s=open(svgfile).read()
    out={}
    for gid in ['jade','red','gold','ink']:
        m=re.search(r'<g id="%s"[^>]*>(.*?)</g>'%gid, s, re.S)
        out[gid]=[]
        for p in re.findall(r'<path ([^>]*)/>', m.group(1)):
            d=re.search(r' d="([^"]*)"',' '+p).group(1)
            out[gid].append((p,d))
    return out
