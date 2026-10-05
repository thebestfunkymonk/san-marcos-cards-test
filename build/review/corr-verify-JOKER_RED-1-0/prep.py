import sys
import xml.etree.ElementTree as ET
ET.register_namespace('', 'http://www.w3.org/2000/svg')
src, out = sys.argv[1], sys.argv[2]
keep = sys.argv[3] if len(sys.argv) > 3 else None
t = ET.parse(src)
root = t.getroot()
def strip(parent):
    for el in list(parent):
        c = el.get('class') or ''
        if 'index' in c or c == 'stock':
            parent.remove(el)
        else:
            strip(el)
strip(root)
if keep:
    for g in list(root):
        if g.tag.endswith('g') and g.get('id') not in keep.split(','):
            root.remove(g)
t.write(out)
