For purposes of creating UO images on Ubuntu web servers. UOP support not planned.

Do I know what I'm doing? No. Do you? Then do something about it and make a pull request.

Written with python 3.6.6

Install requirements with `pip install -r requirements.txt`

Example of creating an image:

```
from ultimapy.ascii_font import ASCIIFont

img = ASCIIFont.FONTS[3].get_string_image("Hello world")
img.save("HelloWorld.bmp")

from ultimapy.animations import Animation

red = 32
south = 1
just_standing_there = 0
only_give_me_the_first_frame = True
# args don't need to be explicitly specified, but for the sake of an example...
img_frame = Animation.get_animation(body=400, action=just_standing_there, direction=south, hue=red, only_give_me_the_first_frame)
img = img_frame[0].bitmap  # there will only be an index of 1 if you only ask for the first frame
img.save("red_guy.bmp")
```