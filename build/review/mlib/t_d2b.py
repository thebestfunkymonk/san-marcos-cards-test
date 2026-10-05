from rh import *
from deck.motifs import geometric as M
cn = M.source_rosette(375, 525, 130)
print("C_N rosette: symdiff vs rot180", round(cn.shape().symmetric_difference(cn.rot180().shape()).area, 2), "px2")
d2 = M.source_rosette(375, 525, 40, twist=False, w=T.MEDIUM)
both = d2 + d2.mirror_x().recolor(T.RED)
show(d2.recolor(T.INK) , "d2-r40-6x", zoom=6)
# overlay: rosette in ink, its mirror in red -> where only one colour shows, it is asymmetric
show(d2.mirror_x().recolor(T.RED) + d2, "d2-r40-vs-mirror-6x", zoom=6)
