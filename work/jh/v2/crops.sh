#!/bin/bash
# 3x crops of the JH draft: head, plume, bow hand, fiddle top, fiddle body, chest
cd /home/luke/Projects/design/san-marcos-deck
O=work/jh/v2/out
I=$O/JH-3x.png
magick $I -crop 600x540+960+165 +repage $O/c_plume.png
magick $I -crop 540x600+870+330 +repage $O/c_face.png
magick $I -crop 420x540+630+1080 +repage $O/c_bowhand.png
magick $I -crop 480x600+1350+400 +repage $O/c_fidtop.png
magick $I -crop 480x660+1350+860 +repage $O/c_fidbody.png
magick $I -crop 600x660+780+840 +repage $O/c_chest.png
