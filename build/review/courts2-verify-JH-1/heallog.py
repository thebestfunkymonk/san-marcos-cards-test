import warnings
warnings.simplefilter("always")
from art import JH
from deck import courtkit as K
K.HAND_LOG.clear()
sc = JH.figure()
sc.layers()
print("HAND_LOG", K.HAND_LOG)
print(len(sc.heal_log))
for e in sc.heal_log: print(" ", e)
