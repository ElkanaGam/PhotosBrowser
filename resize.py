from pathlib import Path
from PIL import Image

header = r'C:\Users\elkana\Pictures'
img_name = r'C:\Users\elkana\Pictures\ot.png'
out = header+'\_thumbnail22.jpg'
im = Image.open(img_name)

dpi = im.info['dpi']
# im.show()
im = im.convert('RGB')
rot = im.rotate(angle=90, expand = True)
rot.thumbnail((200,300), Image.ANTIALIAS)

rot.save(out, "JPEG",dpi = dpi)
print(out)
im = Image.open(out)
im.show()