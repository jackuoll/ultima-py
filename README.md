[![PyPI version](https://badge.fury.io/py/ultimapy.svg)](https://badge.fury.io/py/ultimapy)

## ultimapy

ultimapy is a python library for rendering images from the Ultima Online client files. The SDK part of the project is almost a direct 1:1 code translation of the C# Ultima SDK (used by UOFiddler, among other things).

It does not support saving back to client files, only reading.

### Why?

The C# SDK does not run with mono due to implementations being missing from the underlying libraries. Attempts to get this to run in dotnet core or using mono have never been successful. Rewriting this code in Python allows the code to be used in a linux environment, for the most part out of the box. Since Python has many available popular open source web frameworks, this library allows you to serve up images directly in code used by your web framework of choice.

It also includes some features not seen anywhere else, such as the rendering of player avatars. Items & paperdolls have been done before in PHP, but that code is difficult to read and edit, whereas this library takes a much more flexible and simple approach (the same as which is used in the C# SDK). This lib even fixes a few rendering bugs which are present in the C# SDK.

### Features
ultimapy can currently do the following:
* Render land, statics. This includes rendering of in game items.
* Render "animations" or single frames of animations. This includes monsters and players, though player construction is done by rendering the mount, body, hair and clothing layers in order.
* Draw text from the client (eg, ASCIIFont).
* Extract information about skills - naming, groups, indexes.
* Rendering paperdolls / individual gumps

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
from ultimapy.sdk.art import Art
from ultimapy.sdk.hues import Hues

moongate_item_id = 0x0F6C
art = Art.get_static(moongate_item_id, check_max_id=False)
art.save("art.png")

red = Hues.HUES[32]
red_hued_art = red.apply_to(art, only_grey_pixels=False)
red_hued_art.save("red_art.png")
```
