from struct import unpack

from PIL import Image

from .bodies import *
from .file_index import FileIndex
from .hues import Hues
from .tile_data import item_data
from .utils import get_arbg_from_16_bit, is_mount, mount_info, paste_centered, trim


class Animation:
    table = {}
    _file_indexes = [
        FileIndex("anim.idx", "anim.mul", 0x40000, 6),
        FileIndex("anim2.idx", "anim2.mul", 0x10000, -1),  # i don't have these files to test anything
        FileIndex("anim3.idx", "anim3.mul", 0x20000, -1),  # i don't have these files to test anything
        FileIndex("anim4.idx", "anim4.mul", 0x20000, -1),
        FileIndex("anim5.idx", "anim5.mul", 0x20000, -1)
    ]

    @classmethod
    def get_animation(cls, body, action, direction, hue, first_frame, partial_hue=False):
        body, hue = cls.translate(body, hue)
        spectral_shade = hue & 0x4000 != 0
        body, file_type = BodyConverter.convert(body)
        file_index, index = cls.get_file_index(body, action, direction, file_type)
        stream, length, extra, patched = file_index.seek(index)
        if not stream:
            return None
        flip = direction > 4
        palette = [x ^ 0x8000 for x in unpack('H' * 256, stream.read(2 * 256))]
        start = stream.tell()
        frame_count = unpack('i', stream.read(4))[0]
        frames = [None] * frame_count
        lookups = [start + x for x in unpack('i' * frame_count, stream.read(4 * frame_count))]
        hue = (hue & 0x3FFF) - 1
        hue_obj = None
        if spectral_shade:
            hue = 0x4001
        if hue in Hues.HUES:
            hue_obj = Hues.HUES[hue]
        if first_frame:
            frame_count = 1
        for i in range(frame_count):
            stream.seek(lookups[i])
            frames[i] = Frame(palette, stream, flip)
            if hue_obj and frames[i] and frames[i].bitmap:
                frames[i].bitmap = hue_obj.apply_to(frames[i].bitmap, partial_hue)
        return frames

    @classmethod
    def load_table(cls):
        count = int(400 + (cls._file_indexes[0].index_length - 35000) / 175)
        cls.table = {i: None for i in range(count)}
        for i in range(count):
            bte = BodyTable.entries.get(i, None)
            if bte is None or BodyConverter.contains(i):
                cls.table[i] = i
            else:
                cls.table[i] = bte.old_id | (1 << 31) | ((bte.new_hue & 0xFFFF) << 15)

    @classmethod
    def translate(cls, body, hue=None):
        if not cls.table:
            cls.load_table()
        if body <= 0 or body >= len(cls.table):
            return 0, 0
        t = cls.table[body]  # except?
        body = t & 0x7FFF
        if hue is None:
            return body, 0
        if t & (1 << 31) != 0:
            vhue = (hue & 0x3FFF) - 1
            if vhue not in Hues.HUES:
                hue = (t >> 15) & 0xFFFF
        return body, hue

    @classmethod
    def is_action_defined(cls, body, action, direction):
        body, _ = cls.translate(body)
        body, file_type = BodyConverter.convert(body)
        file_index, index = cls.get_file_index(body, action, direction, file_type)
        valid, length, _, _ = file_index.valid(index)
        return valid and length > 0

    @classmethod
    def is_anim_defined(cls, body, action, direction, file_type):
        file_index, index = cls.get_file_index(body, action, direction, file_type)
        stream, length, _, _ = file_index.seek(index)
        return stream and length > 0

    @classmethod
    def get_anim_count(cls, file_type):
        if file_type == 2:
            info = [200, cls._file_indexes[file_type-1].index_length - 22000 * 12, 12 * 65]
        else:
            if file_type not in range(6):
                file_type = 1
            info = [400, cls._file_indexes[file_type-1].index_length - 35000 * 12, 12 * 175]
        return info[0] + info[1] / info[2]

    @classmethod
    def get_anim_length(cls, body, file_type):
        if file_type not in [1, 2, 3, 4, 5]:
            file_type = 1
        if file_type in [1,4,5]:
            return 22 if body < 200 else 13 if body < 400 else 35
        if file_type == 2:
            return 22 if body < 200 else 13
        if file_type == 3:
            return 13 if body < 300 else 22 if body < 400 else 35
        return 0

    @classmethod
    def get_file_index(cls, body, action, direction, file_type):
        if file_type not in [1,2,3,4,5]:
            file_type = 1
        file_idx = cls._file_indexes[file_type-1]
        index = None
        if file_type == 1:
            if body < 200:
                index = body * 110
            elif body < 400:
                index = 22000 + (body - 200) * 65
            else:
                index = 35000 + (body - 400) * 175
        elif file_type == 2:
            if body < 200:
                index = body * 110
            else:
                index = 22000 + (body - 200) * 65
        elif file_type == 3:
            if body < 300:
                index = body * 65
            elif body < 400:
                index = 33000 + (body - 300) * 110
            else:
                index = 35000 + (body - 400) * 175
        elif file_type == 4:
            if body < 200:
                index = body * 110
            elif body < 400:
                index = 22000 + (body - 200) * 65
            else:
                index = 35000 + (body - 400) * 175
        elif file_type == 5:
            if body < 200 and body != 34:
                index = body * 110
            elif body < 400:
                index = 22000 + (body - 200) * 65
            else:
                index = 35000 + (body - 400) * 175

        index += action * 5

        if direction <= 4:
            index += direction
        else:
            index += direction - (direction - 4) * 2

        return file_idx, index

    @classmethod
    def get_file_name(cls, body):
        body = cls.translate(body)
        file_type = BodyConverter.convert(body)
        if file_type == 1:
            return "anim.mul"
        return f"anim{file_type}.mul"

    @classmethod
    def draw_player(cls, female, body_hue, layers, order=True):
        """
        Draw a frame of the passed layers.
        :param female: Avatar is female?
        :param body_hue: Body hue of the player.
        :param layers: List of tuples in the format (ItemID, Hue).
        :param order: Whether to try order them to look correct. If set to false, the list of tuples must be in the
                      order in which you want them rendered. This would be useful if the default ordering does not contain
                      the items in your list.
        :return: A trimmed image of all the layers.
        """
        if not layers:
            return
        mount, mount_hue = mount_info(layers)
        action = 4 if not mount else 25
        img = Image.new("RGBA", (200, 200))
        if mount:
            mount_img = Animation.get_animation(mount, 2, 1, mount_hue, True, True)
            paste_centered(img, mount_img)
        player_frames = Animation.get_animation(401 if female else 400, action, 1, body_hue, True)

        paste_centered(img, player_frames)
        for item_id, hue in filter(lambda layer: not is_mount(layer[0]), layers):
            item = item_data(item_id)
            clothing_frame = Animation.get_animation(item.animation, action, 1, hue, True, item.partial_hue)
            if not clothing_frame:
                continue
            paste_centered(img, clothing_frame)
        return trim(img)


def integer(binary_string):
    return int(binary_string, 2)


class Frame:
    _double_xor = (0x200 << 22) | (0x200 << 12)
    empty = None

    def __init__(self, palette, reader, flip):
        if reader is None:
            self.center = None
            self.bitmap = Image.new('RGBA', (0, 0))
            return
        x_center, y_center, width, height = unpack('h' * 4, reader.read(2 * 4))
        if width == 0 or height == 0:
            return

        self.bitmap = Image.new('RGBA', (width, height))
        x_base = x_center - 0x200
        y_base = y_center + height - 0x200
        header = unpack('i', reader.read(4))[0]
        while header != 0x7FFF7FFF:
            header ^= self._double_xor
            bytes_to_write = header & 0xFFF
            x = ((header >> 22) & 0x3FF) + x_base
            y = ((header >> 12) & 0x3FF) + y_base
            for i in range(bytes_to_write):
                c = palette[ord(reader.read(1))]
                if c != 0:
                    self.bitmap.putpixel((x + i, y), get_arbg_from_16_bit(c))

            header = unpack('i', reader.read(4))[0]
        if flip:
            self.bitmap = self.bitmap.transpose(Image.FLIP_LEFT_RIGHT)
            x_center = width - x_center

        self.center = (x_center, y_center)


# initialize
if not Frame.empty:
    Frame.empty = Frame(None, None, None)
