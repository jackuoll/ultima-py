from struct import unpack

from ultimapy.settings import ultima_file_path

from .utils import get_arbg_from_16_bit


class Hues:
    """
        Results 100% accurate to C# Ultima SDK in the limited testing done.
        Not all methods implemented.
        Should be reconfigured to auto load. Should never need to instantiate anything manually.
    """
    HUES = {}

    @classmethod
    def apply_to(cls, img, color, only_grey_pixels):
        """
            basically a static method for hueing an image.
        :param img: input image
        :param color: arbg color
        :param only_grey_pixels: to be used in conjunction with ItemData -> partial_hue
        :return: hued image
        """
        img = img.copy()
        width = img.size[0]
        height = img.size[1]
        for y in range(height):
            for x in range(width):
                col = img.getpixel((x, y))
                if col == (0, 0, 0, 0):
                    continue
                if col[0] == col[1] == col[2] or not only_grey_pixels:
                    img.putpixel((x, y), color)

        return img

    @classmethod
    def load(cls):
        print("Loading Hues")
        cls.HUES = {i: Hue(i) for i in range(3000)}
        f = open(ultima_file_path('hues.mul'), 'rb')
        block_count = max(375, int(unpack('i', f.read(4))[0] / 708))
        f.seek(0)
        headers = []  # why?
        idx = 0
        for i in range(block_count):
            headers.append(unpack('i', f.read(4)))
            for j in range(8):
                new_hue = Hue(idx)
                new_hue.colors = [x | 0x8000 for x in unpack('H'*32, f.read(64))]
                new_hue.table_start, new_hue.table_end = unpack('hh', f.read(4))
                new_hue.name = f.read(20).decode('cp1252')
                cls.HUES[idx] = new_hue
                idx += 1
        # ethereal hue
        cls.HUES[0x4001] = Hue(0x4001)


class Hue:
    """
        Results 100% accurate to C# Ultima SDK in the limited testing done.
        Not all methods implemented.
    """
    def __init__(self, index):
        self.name = None
        self.index = index
        self.colors = []  # numbers
        self.table_start = 0
        self.table_end = 0

    def apply_to(self, img, only_grey_pixels):
        img = img.copy()
        width = img.size[0]
        height = img.size[1]
        for y in range(height):
            for x in range(width):
                col = img.getpixel((x, y))
                if col == (0, 0, 0, 0):
                    continue
                if col[0] == col[1] == col[2] or not only_grey_pixels:
                    if self.index == 0x4001:
                        img.putpixel((x, y), (0, 0, 0, 200 - col[0]))
                    else:
                        r = int(col[0] / 255 * 31)
                        img.putpixel((x, y), get_arbg_from_16_bit(self.colors[r]))

        return img

if not Hues.HUES:
    Hues.load()