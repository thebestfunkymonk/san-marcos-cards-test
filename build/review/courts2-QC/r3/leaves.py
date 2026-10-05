import sys
sys.path.insert(0, "art")
import QC
from deck import courtkit as K
sc, fc = QC.figure()
it = {i.name: i for i in sc.items}
g = [i for i in sc.items if i.name == "gown"][0]
import _qc_gown as GW
