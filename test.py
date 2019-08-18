from ultimapy.sdk.animations import Animation
from ultimapy.sdk.hues import Hues
from PIL import Image, ImageOps

get_anim = Animation.get_animation


def draw_body(partial=False):
    return get_anim(220, 0, 2, 0x4000, True, partial)[0].bitmap

black = (255, 255, 255, 255)
img = draw_body()
img.show()
to_put = Image.new('RGBA', img.size, color=(0, 0, 0, 255))
print(img.getpixel((1, 1)))
for x in range(img.size[0]):
    for y in range(img.size[1]):
        new_pix = cur_pix = img.getpixel((x, y))
        if cur_pix != (0, 0, 0, 0):
            new_pix = (cur_pix[2], cur_pix[2], cur_pix[2], 255 - cur_pix[2])
        to_put.putpixel((x, y), new_pix)


bg = Image.open('/home/jack/projects/bg.png')
blah = Image.new('RGBA', bg.size, color=(0, 0, 0, 0))
blah.paste(to_put, (130, 120))
#Image.composite(blah, bg, mask=blah).show()
