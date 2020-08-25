from PIL import Image

from ultimapy.settings import ultima_file_path

from .utils import get_arbg_from_16_bit, read_byte


class ASCIIFont:
    """
        Results 100% accurate to C# Ultima SDK in the limited testing done.
        Some methods not implemented.
        Should be reconfigured to auto load. Should never need to instantiate anything manually.
    """
    FONTS = []

    def __init__(self, buffer):
        self.header = ord(buffer.read(1))
        self.height = 0
        self.characters = {} # letter, image
        ASCIIFont.FONTS.append(self)

    @classmethod
    def load(cls):
        with open(ultima_file_path('fonts.mul'), 'rb') as f:
            for i in range(10):
                font = ASCIIFont(f)
                for k in range(224):
                    width = read_byte(f)
                    height = read_byte(f)
                    read_byte(f)  # unknown, discard
                    if k < 96:
                        font.height = max(font.height, height)
                    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
                    pos = f.tell()
                    stride = 2 * width  # 2 bytes, width
                    for y in range(height):
                        f.seek(pos)
                        pos += stride
                        for x in range(width):
                            first_byte = read_byte(f)
                            second_byte = read_byte(f)
                            pixel_num = first_byte | (second_byte << 8)
                            if pixel_num > 0:
                                img.putpixel((x, y), get_arbg_from_16_bit(pixel_num ^ 0x8000))
                    font.add_character(chr(k + 32), img)

    def add_character(self, letter, character):
        self.characters[letter] = character

    def get_character(self, letter):
        return self.characters[letter]

    def character_image_list(self, full_string):
        return [self.characters[letter] for letter in full_string]

    def get_width(self, full_string):
        img_list = self.character_image_list(full_string)
        total_width = sum(img.width for img in img_list)
        return total_width + 2

    def get_string_image(self, full_string):
        width = self.get_width(full_string)
        height = self.height + 2
        new_im = Image.new('RGBA', (width, height))
        x_offset = 2
        for im in self.character_image_list(full_string):
            new_im.paste(im, (x_offset, height - im.size[1]))
            x_offset += im.size[0]
        return new_im


ASCIIFont.load()
