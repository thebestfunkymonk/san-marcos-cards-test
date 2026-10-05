import sys
from PIL import Image
import numpy as np
from scipy import ndimage
a=np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(int); b=np.asarray(Image.open(sys.argv[2]).convert('RGB')).astype(int)
d=(np.abs(a-b).sum(2)>40)
lab,n=ndimage.label(ndimage.binary_dilation(d,iterations=6))
for s in ndimage.find_objects(lab):
    y,x=s; print('card box', x.start//3, y.start//3, x.stop//3, y.stop//3)
