import os
from struct import unpack

from PIL import Image

from ultimapy.settings import ultima_file_path


UNICODE_SPACE_WIDTH = 8
MAX_FONTS = 20
MAX_GLYPHS = 0x10000


class UnicodeGlyph:
    __slots__ = ('offset_x', 'offset_y', 'width', 'height', 'data')

    def __init__(self, offset_x, offset_y, width, height, data):
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.width = width
        self.height = height
        self.data = data


class UnicodeFont:
    FONTS = [None] * MAX_FONTS

    def __init__(self, font_index, file_path):
        self.font_index = font_index
        self.file_path = file_path
        self.glyphs = {}

    def _load_glyph(self, index):
        with open(self.file_path, 'rb') as f:
            f.seek(index * 4)
            raw = f.read(4)
            if len(raw) < 4:
                return None
            offset = unpack('<i', raw)[0]
            if offset == 0:
                return None

            f.seek(offset)
            header = f.read(4)
            if len(header) < 4:
                return None

            offset_x, offset_y, width, height = unpack('<bbbb', header)

            if width <= 0 or height <= 0:
                return None

            scanline_bytes = ((width - 1) // 8) + 1
            data = f.read(scanline_bytes * height)
            if len(data) < scanline_bytes * height:
                return None

            return UnicodeGlyph(offset_x, offset_y, width, height, data)

    def get_glyph(self, char):
        index = ord(char) if isinstance(char, str) else char
        if index < 0 or index >= MAX_GLYPHS:
            return None
        if index not in self.glyphs:
            self.glyphs[index] = self._load_glyph(index)
        return self.glyphs[index]

    def get_character(self, char):
        glyph = self.get_glyph(char)
        if glyph is None:
            return Image.new("RGBA", (0, 0), (0, 0, 0, 0))
        return _glyph_to_image(glyph)

    def get_width(self, text):
        total = 0
        for ch in text:
            if ch == ' ':
                total += UNICODE_SPACE_WIDTH
            elif ch == '\n' or ch == '\r':
                continue
            else:
                glyph = self.get_glyph(ch)
                if glyph is not None:
                    total += glyph.offset_x + glyph.width + 1
        return total

    def get_height(self, text):
        max_h = 0
        for ch in text:
            glyph = self.get_glyph(ch)
            if glyph is not None:
                h = glyph.offset_y + glyph.height
                if h > max_h:
                    max_h = h
        return max_h

    def get_string_image(self, text, color=(255, 255, 255, 255), border=False,
                         border_color=(1, 1, 1, 255)):
        if not text:
            return Image.new("RGBA", (0, 0), (0, 0, 0, 0))

        lines = text.split('\n')
        line_images = []
        total_width = 0
        total_height = 0

        for line in lines:
            width = self.get_width(line)
            height = self.get_height(line) if line else 0
            if height < 14:
                height = 14
            if width > total_width:
                total_width = width
            total_height += height
            line_images.append((line, width, height))

        if total_width <= 0:
            return Image.new("RGBA", (0, 0), (0, 0, 0, 0))

        pad = 2 if border else 0
        img = Image.new("RGBA", (total_width + 2 + pad, total_height + 2 + pad), (0, 0, 0, 0))
        ox = 1 if border else 0
        oy = 1 if border else 0

        if border:
            for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
                y_offset = oy + dy
                for line, line_width, line_height in line_images:
                    x = ox + dx
                    for ch in line:
                        if ch == ' ':
                            x += UNICODE_SPACE_WIDTH
                            continue
                        if ch == '\r':
                            continue
                        glyph = self.get_glyph(ch)
                        if glyph is None:
                            continue
                        char_img = _glyph_to_image(glyph, border_color)
                        img.paste(char_img, (x + glyph.offset_x, y_offset + glyph.offset_y), char_img)
                        x += glyph.offset_x + glyph.width + 1
                    y_offset += line_height

        y_offset = oy
        for line, line_width, line_height in line_images:
            x = ox
            for ch in line:
                if ch == ' ':
                    x += UNICODE_SPACE_WIDTH
                    continue
                if ch == '\r':
                    continue

                glyph = self.get_glyph(ch)
                if glyph is None:
                    continue

                char_img = _glyph_to_image(glyph, color)
                img.paste(char_img, (x + glyph.offset_x, y_offset + glyph.offset_y), char_img)
                x += glyph.offset_x + glyph.width + 1

            y_offset += line_height

        return img

    @classmethod
    def load(cls):
        for i in range(MAX_FONTS):
            name = "unifont.mul" if i == 0 else f"unifont{i}.mul"
            path = ultima_file_path(name)
            if os.path.exists(path):
                cls.FONTS[i] = UnicodeFont(i, path)
        # fallback: if font 1 is missing, copy font 0
        if cls.FONTS[1] is None and cls.FONTS[0] is not None:
            cls.FONTS[1] = cls.FONTS[0]


def _glyph_to_image(glyph, color=(255, 255, 255, 255)):
    img = Image.new("RGBA", (glyph.width, glyph.height), (0, 0, 0, 0))
    scanline_bytes = ((glyph.width - 1) // 8) + 1
    data = glyph.data

    for y in range(glyph.height):
        row_offset = y * scanline_bytes
        for byte_idx in range(scanline_bytes):
            byte_val = data[row_offset + byte_idx]
            if byte_val == 0:
                continue
            base_x = byte_idx << 3
            for bit in range(8):
                x = base_x + bit
                if x >= glyph.width:
                    break
                if byte_val & (1 << (7 - bit)):
                    img.putpixel((x, y), color)

    return img


UnicodeFont.load()
