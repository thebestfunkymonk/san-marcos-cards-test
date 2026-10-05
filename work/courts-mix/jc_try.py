import os, sys
ART = '/home/luke/Projects/design/san-marcos-deck/art'
sys.path.insert(0, ART)
import JC
import _jc_face as F
from deck import courtkit as K
V = os.environ.get('JCV', 'kit')
_orig = F.face_jc
if V == 'kit':
    def fj(center, **kw):
        return K.face(center, '3/4-left', age='young', lids='raised', pupil_dx=-3.0)
    F.face_jc = fj
def build():
    return JC.figure().layers()
