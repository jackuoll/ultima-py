from struct import unpack

from PIL import Image

from ultimapy.sdk.file_index import FileIndex
from ultimapy.sdk.hues import Hues
from ultimapy.sdk.tile_data import item_data

from .utils import get_arbg_from_16_bit, trim


class Gumps:
    _file_index = FileIndex("gumpidx.mul", "gumpart.mul", 0xFFFF, 12)
    _cache = [None] * 0xFFFF
    _removed = [False] * 0xFFFF
    _patched = {}

    @classmethod
    def get_gump(cls, index, hue=0, partial_hue=False):
        def read_number():
            return unpack('h', stream.read(2))[0]

        cached = cls._cache[index]
        if cached:
            return cls.hue_gump(cached, hue, partial_hue)

        stream, length, extra, patched = cls._file_index.seek(index)
        if not stream or extra == -1:
            return
        width = (extra >> 16) & 0xFFFF
        height = extra & 0xFFFF
        if not width or not height:
            return

        orig_pos = stream.tell()
        lookups = [0] * height
        for i in range(height):
            lookups[i] = unpack('i', stream.read(4))[0] * 4

        bitmap = Image.new("RGBA", (width, height))
        for y in range(height):
            x = 0
            stream.seek(orig_pos + lookups[y])
            while x < width:
                color, x_run = read_number(), read_number()
                if color != 0:
                    color ^= 0x8000
                    for pix in range(x_run):
                        bitmap.putpixel((x + pix, y), get_arbg_from_16_bit(color))
                x += x_run
        cls._cache[index] = bitmap
        return cls.hue_gump(bitmap, hue, partial_hue)

    @classmethod
    def hue_gump(cls, bitmap, hue, partial_hue):
        copy = bitmap.copy()
        if hue:
            hue = (hue & 0x3FFF) - 1
            return Hues.HUES[hue].apply_to(copy, only_grey_pixels=partial_hue)
        return copy


    def paperdoll_of(self, female, body_hue, layers, order=True):
        """
            Draw a paperdoll of the passed layers.
            :param female: Avatar is female?
            :param body_hue: Body hue of the player.
            :param layers: List of tuples in the format (ItemID, Hue).
            :param order: Whether to try order them to look correct. If set to false, the list of tuples must be in the
                          order in which you want them rendered. This would be useful if the default ordering does not contain
                          the items in your list.
            :return: A trimmed image of all the layers.
            """
        img = Image.new("RGBA", (260, 237))
        body = 12 + int(female)
        body_img = get_gump(body, body_hue, True)
        img.paste(body_img)

        for item_id, hue in layers:
            item = item_data(item_id)
            anim = item.animation
            partial = item.partial_hue
            item = get_gump(anim + 50000 + int(female) * 10000, hue, partial) or get_gump(anim + 50000, hue, partial)
            if not item:
                continue
            img.paste(item, (0, 0), item)
        trimmed = trim(img)
        return trimmed


get_gump = Gumps.get_gump
