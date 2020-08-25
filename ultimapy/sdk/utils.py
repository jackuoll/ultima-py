from PIL import Image, ImageChops

from ultimapy.settings import ULTIMA_MOUNT_IDS


def paste_centered(parent_image, input_frame, frame_no=0):
    """
    :param parent_image: bitmap to be pasted onto
    :param input_frame: ultimapy.animations.Frame
    :param frame_no: the frame number
    """
    if not input_frame or len(input_frame) <= frame_no:
        return
    input_frame = input_frame[frame_no]
    new_center = (100 - input_frame.center[0], 100 - input_frame.center[1] - input_frame.bitmap.size[1])
    parent_image.paste(input_frame.bitmap, new_center, input_frame.bitmap)


def trim(im):
    """Trim an image of surrounding transparency"""
    bg = Image.new(im.mode, im.size, im.getpixel((0, 0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)


def read_byte(buf):
    """Should be removed."""
    return ord(buf.read(1))


def safe_list_get(lst, idx, default):
    try:
        return lst[idx]
    except IndexError:
        return default


def get_arbg_from_16_bit(sixteen):
    """Should be refactored."""
    def get_arbg(num):
        num = num * 255 / 31
        num = round(num)
        return num
    blue = get_arbg(sixteen & 31)
    green = get_arbg((sixteen >> 5) & 31)
    red = get_arbg((sixteen >> 10) & 31)
    alpha = ((sixteen >> 15) & 1) * 255
    return red, green, blue, alpha


def is_mount(item_id):
    return int(item_id) in ULTIMA_MOUNT_IDS


def mount_info(layers):
    for item_id, hue in layers:
        if is_mount(item_id):
            return item_id, hue
    return None, None