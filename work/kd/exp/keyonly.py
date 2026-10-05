import sys; sys.path.insert(0,'/home/luke/Projects/design/san-marcos-deck')
from deck import courtkit as K
from art import _kd_body as B
def figure():
    sc = K.Scene()
    sc.part("key", B.key_of_ford(552.0, bow_c=(552.0,124.0), ring_r=(40.0,30.5), star_r=30.5, star_w=11.5, core_r=7.2, stem_hw=10.0, collar_hw=14.5, collars=(174.0,250.0,326.0)))
    return sc
