import functools
from struct import unpack

from ultimapy.settings import ultima_file_path

from .art import Art


class TileData:
    loaded = False
    land_header = [0] * 512
    land_data = [None] * 0x4000
    item_header = []
    item_data = []
    height_table = []
    new_format = False

    @classmethod
    def load(cls):
        cls.loaded = True
        with open(ultima_file_path('tiledata.mul'), 'rb') as f:
            f.seek(0, 2)
            length = f.tell()
            f.seek(0)
            cls.new_format = Art.is_uoahs
            j = 0
            for i in range(0, len(cls.land_data), 32):
                cls.land_header[j] = unpack('i', f.read(4))[0]
                j += 1
                for count in range(32):
                    mul_type = NewLandMul if cls.new_format else OldLandMul
                    cls.land_data[i + count] = mul_type.from_stream(f)

            remaining = length - f.tell()
            mul_type = NewItemMul if cls.new_format else OldItemMul
            cls.item_header = [0] * int(remaining / (mul_type.size * 32 + 4))
            item_length = len(cls.item_header) * 32
            cls.item_data = [None] * item_length
            cls.height_table = [0] * item_length
            j = 0
            for i in range(0, item_length, 32):
                cls.item_header[j] = unpack('i', f.read(4))[0]
                j += 1
                for count in range(32):
                    cls.item_data[i + count] = mul_type.from_stream(f)


class OldLandMul:
    def __init__(self, flags, tex_id, name):
        self.flags = flags
        self.texID = tex_id
        self.name = name.decode('cp1252')

    @classmethod
    def from_stream(cls, stream):
        return OldLandMul(*unpack('ih20s', stream.read(4 + 2 + 20)))


class NewLandMul(OldLandMul):
    def __init__(self, flags, unk1, tex_id, name):
        super().__init__(flags, tex_id, name)
        self.unk1 = unk1

    @classmethod
    def from_stream(cls, stream):
        return NewLandMul(*unpack('iih20s', stream.read(4 + 4 + 2 + 20)))


class OldItemMul:
    size = 4 + 1 * 9 + 2 * 2 + 20

    @property
    @functools.lru_cache()
    def partial_hue(self):
        return self.flags & 0x00040000

    def __init__(self, flags, weight, quality, misc, unk2, amt, anim, unk3, hue, stacking_offset, value, height, name):
        self.flags = flags
        self.weight = int(weight)
        self.quality = int(quality)
        self.misc = misc
        self.unk2 = int(unk2)
        self.quantity = int(amt)
        self.animation = anim
        self.unk3 = int(unk3)
        self.hue = int(hue)
        self.stacking_offset = int(stacking_offset)
        self.value = int(value)
        self.height = int(height)
        self.name = name.decode('cp1252')
        self.name = self.name.replace("\x00", "")

    @classmethod
    def from_stream(cls, stream):
        return OldItemMul(*unpack('ibbhbbhbbbbb20s', stream.read(cls.size)))


class NewItemMul(OldItemMul):
    size = 4 * 2 + 1 * 9 + 2 * 2 + 20

    def __init__(self, flags, unk1, weight, quality, misc, unk2, amt, anim, unk3, hue, stacking_offset, value, height, name):
        super().__init__(flags, weight, quality, misc, unk2, amt, anim, unk3, hue, stacking_offset, value, height, name)
        self.unk1 = unk1

    @classmethod
    def from_stream(cls, stream):
        return NewItemMul(*unpack('iibbhbbhbbbbb20s', stream.read(cls.size)))


if not TileData.loaded:
    TileData.load()


def item_data(index):
    return TileData.item_data[index]


def land_data(index):
    return TileData.land_data[index]
