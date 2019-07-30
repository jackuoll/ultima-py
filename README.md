## ultimapy

ultimapy is a python library for rendering images from the Ultima Online client files. The SDK part of the project is almost a direct 1:1 code translation of the C# Ultima SDK (used by UOFiddler, among other things).

###Features
ultimapy can currently do the following:
* Render land, statics. This includes rendering of in game items.
* Render "animations" or single frames of animations. This includes monsters and players, though player construction is done by rendering the mount, body, hair and clothing layers in order.
* Draw text from the client (eg, ASCIIFont).
* Extract information about skills - naming, groups, indexes.

#####Unimplemented features
######Planned
* Rendering gumps
* Rendering paperdolls (requires gumps)
* Command to fully set up ultimapy - downloading compatible client files and auto generating your environment to make getting going on your website easy.

######Unplanned
* UOP support is not planned, which limits the client version.



### Installation
Install ultimapy to your project with:

`pip install ultimapy`

You must specify your Ultima Online client directory by any of the following methods:

* `environment.ini` - add the line `ULTIMA_FILES_DIR=/path/to/ultima `
* Django - add into settings.py: `ULTIMA_FILES_DIR=/path/to/ultima`
* Specify an environment variable `ULTIMA_FILES_DIR` with the value `/path/to/ultima`

### Settings
As above, settings can be set through any of the methods that the `ULTIMA_FILES_DIR` can be set by (`environment.ini`, Django settings, environment variable).

Currently there are only 2 settings:
* `ULTIMA_FILES_DIR`, this is the path to your Ultima Online directory. This has no default and will not read from registry.
* `ULTIMA_MOUNT_IDS`, if loaded via environment, should be a valid json list of all possible mount IDs. If set in Django, can simply be set up as a list. This has a default of mounts that are found in the 5.0.8.3 client.


### How to use ultimapy

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
img_frame = Animation.get_animation(body=400, action=just_standing_there, direction=south, hue=red, first_frame=only_give_me_the_first_frame)
img = img_frame[0].bitmap  # there will only be an index of 1 if you only ask for the first frame
img.save("red_guy.bmp")
```

#####This section is in progress, as there is a sole developer of this project, and work on this project is purely fueled by requirements of https://uolostlands.com 