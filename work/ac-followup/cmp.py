import sys
from PIL import Image
names = sys.argv[2:]; f = sys.argv[1] if sys.argv[1] != '-' else 'wreath_3x.png'
ims = [Image.open(f'work/ac-followup/out/{n}/{f}') for n in names]
im = Image.new('RGB', (max(i.width for i in ims), sum(i.height for i in ims)), 'white'); y = 0
for i in ims: im.paste(i, (0, y)); y += i.height
im.save(f'work/ac-followup/out/cmp_{"_".join(names)}.png'); print(f'work/ac-followup/out/cmp_{"_".join(names)}.png')
