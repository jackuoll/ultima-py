from struct import unpack

from PIL import Image

from .file_index import FileIndex
from .utils import get_arbg_from_16_bit


class Art:
    _file_index = FileIndex("artidx.mul", "art.mul", 0x10000, 4)
    idx_length = 0
    _max_item_id = 0
    is_uoahs = False
    _cache = [None] * 0xFFFF
    _removed = [False] * 0xFFFF
    _patched = {}
    _modified = False

    class CheckSums:
        checksum = []
        pos = 0
        length = 0
        index = 0

    checksums_land = []
    checksums_static = []

    @classmethod
    def load(cls):
        cls.idx_length = cls._file_index.index_length / 12
        cls.is_uoahs = cls.idx_length >= 0x13FDC
        cls._max_item_id = 0xFFF if cls.idx_length >= 0x13FDC else 0x7FFF if cls.idx_length == 0xC000 else 0x3FFF

    @classmethod
    def get_legal_item_id(cls, item_id, check_max_id=True):
        if item_id < 0:
            return 0
        if check_max_id:
            if item_id > cls._max_item_id:
                return 0
        return item_id

    @classmethod
    def replace_static(cls, index, bitmap):
        index = cls.get_legal_item_id(index)
        index += 0x4000
        cls._cache[index] = bitmap
        cls._removed[index] = False
        if index in cls._patched:
            del cls._patched[index]
        cls._modified = True

    @classmethod
    def replace_land(cls, index, bitmap):
        index &= 0x3FFF  # 14 bits
        cls._cache[index] = bitmap
        cls._removed[index] = False
        if index in cls._patched:
            del cls._patched[index]
        cls._modified = True

    @classmethod
    def remove_static(cls, index):
        index = cls.get_legal_item_id(index)
        index += 0x4000
        cls._removed[index] = True
        cls._modified = True

    @classmethod
    def remove_land(cls, index):
        index &= 0x3FFF
        cls._removed[index] = True
        cls._modified = True

    @classmethod
    def is_valid_static(cls, index):
        index = cls.get_legal_item_id(index)
        index += 0x4000
        if cls._removed[index]:
            return False
        if cls._cache[index]:
            return True
        stream, length, extra, patched = cls._file_index.seek(index)
        if not stream:
            return False
        stream.seek(4)
        dat = unpack('H' * 4, stream.read(2) * 4)
        # todo: really need to check the output. c# appears to check a byte past the end of the array.
        # todo: also it seems to read 1 byte shorts?
        for short in dat:
            if short <= 0:
                return False
        return True

    @classmethod
    def is_valid_land(cls, index):
        index &= 0x3FFF
        if cls._removed[index]:
            return False
        if cls._cache[index]:
            return True
        return cls._file_index.valid(index)

    @classmethod
    def get_land(cls, index):
        """
        :return: bitmap, patched (bool)
        """
        index &= 0x3FFF
        patched = index in cls._patched
        if cls._removed[index]:
            return None, patched
        cache = cls._cache[index]
        if cache:
            return cache, patched
        stream, length, extra, patched = cls._file_index.seek(index)
        if not stream:
            return None, patched
        if patched:
            cls._patched[index] = True
        caching_data = True  # todo: c# this is Files.CacheData, but it's a static bool that's always true
        if caching_data:
            cls._cache[index] = cls.load_land(stream)
            return cls._cache[index], patched
        return cls.load_land(stream), patched

    @classmethod
    def get_raw_land(cls, index):
        """
            Must be used internally by UOFiddler?
        :return: bytes --
        """
        index &= 0x3FFF
        stream, length, extra, patched = cls._file_index(index)
        if not stream:
            return None
        return stream.read(length)

    @classmethod
    def get_static(cls, index, check_max_id=True):
        """
            todo: this method is almost exactly the same as get_land
        :return: bitmap, patched (bool)
        """
        index = cls.get_legal_item_id(index, check_max_id)
        index += 0x4000
        patched = index in cls._patched
        if cls._removed[index]:
            return None, patched
        cache = cls._cache[index]
        if cache:
            return cache
        stream, length, extra, patched = cls._file_index.seek(index)
        if not stream:
            return None, patched
        if patched:
            cls._patched[index] = True
        caching_data = True  # todo: c# this is Files.CacheData, but it's a static bool that's always true
        if caching_data:
            cls._cache[index] = cls.load_static(stream)
            return cls._cache[index]
        return cls.load_static(stream)

    @classmethod
    def get_raw_static(cls, index):
        """
            Must be used internally by UOFiddler?
        :return: bytes --
        """
        index = cls.get_legal_item_id(index)
        index += 0x4000
        stream, length, extra, patched = cls._file_index.seek(index)
        if not stream:
            return None
        return stream.read(length)

    # measure(bitmap) not implemented - Must be used internally by UOFiddler

    @classmethod
    def load_static(cls, stream):
        def read_number():
            return unpack('h', stream.read(2))[0]

        orig_pos = stream.tell()
        stream.seek(4, 1)

        width, height = read_number(), read_number()
        if width == 0 or height == 0:
            return None
        lookups = [0] * height
        for i in range(height):
            lookups[i] = (height + 4 + read_number()) * 2

        bitmap = Image.new("RGBA", (width, height))

        for y in range(height):
            stream.seek(orig_pos + lookups[y])
            x_offset, x_run = read_number(), read_number()
            x = 0
            while x_offset + x_run != 0:
                if x_offset > width:
                    break
                x += x_offset
                if x_offset + x_run > width:
                    break
                for pix in range(x_run):
                    val = read_number() ^ 0x8000
                    bitmap.putpixel((x + pix, y), get_arbg_from_16_bit(val))
                x += x_run
                x_offset, x_run = read_number(), read_number()
        return bitmap

    @classmethod
    def load_land(cls, stream):
        def read_number(byte_length):
            if byte_length == 1:
                return ord(stream.read(1))
            return unpack('h', stream.read(2))[0]

        bitmap = Image.new("RGBA", (44, 44))

        x_offset = 21
        x_run = 2
        for y in range(22):
            for x in range(x_run):
                bitmap.putpixel((x + x_offset, y), get_arbg_from_16_bit(read_number(2) | 0x8000))
            x_offset -= 1
            x_run += 2

        x_offset = 0
        x_run = 44
        for y in range(22):
            for x in range(x_run):
                bitmap.putpixel((x + x_offset, y + 22), get_arbg_from_16_bit(read_number(2) | 0x8000))
            x_offset += 1
            x_run -= 2

        return bitmap


if Art.idx_length == 0:
    print("Loading art..")
    Art.load()
