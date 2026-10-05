import time, sys
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
from deck import courtkit as K
from deck.motifs import geometric as MG, core as C
reg = K.box(270, 360, 490, 545)
t=time.time(); lat = MG.scale_lattice(reg, 10.0, w=K.MEDIUM); print("lattice", time.time()-t, len(lat.marks))
t=time.time(); ko = C.knockout(K.D(reg), lat); print("knockout", time.time()-t)
t=time.time(); sh = lat.shape(); print("shape", time.time()-t)
