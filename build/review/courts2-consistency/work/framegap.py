from PIL import Image
import numpy as np
D='build/review/courts2-consistency'
def load(v,c): return np.asarray(Image.open(f'{D}/{v}_3x/{c}.png').convert('RGB')).astype(int)
im=load('after','KS')
# find gold rule columns along y=300 near left
row=im[3*300]
for x in range(3*125,3*150):
    pass
paper=im[3*300,3*143]
print('paper sample',paper)
def classify(px):
    return px
# print colours from x=125..150 at y=300
print([tuple(im[3*300,x]) for x in range(3*128,3*146,1)])
