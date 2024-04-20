import ctypes
from struct import unpack

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


def read_int16(buf):
    return unpack('h', buf.read(2))[0]


def read_int32(buf) -> int:
    return unpack('i', buf.read(4))[0]


def read_int64(buf) -> int:
    return unpack('q', buf.read(8))[0]


def read_uint64(buf) -> int:
    return unpack('Q', buf.read(8))[0]



def is_mount(item_id):
    return int(item_id) in ULTIMA_MOUNT_IDS


def mount_info(layers):
    for item_id, hue in layers:
        if is_mount(item_id):
            return item_id, hue
    return None, None


def hash_file_name(s: str):
    eax = 0
    ebx = edi = esi = len(s) + 0xDEADBEEF

    i = 0

    while i + 12 < len(s):
        edi = ((ord(s[i + 7]) << 24) | (ord(s[i + 6]) << 16) | (ord(s[i + 5]) << 8) | ord(s[i + 4])) + edi
        edi = ctypes.c_uint(edi).value
        esi = ((ord(s[i + 11]) << 24) | (ord(s[i + 10]) << 16) | (ord(s[i + 9]) << 8) | ord(s[i + 8])) + esi
        esi = ctypes.c_uint(esi).value
        edx = ((ord(s[i + 3]) << 24) | (ord(s[i + 2]) << 16) | (ord(s[i + 1]) << 8) | ord(s[i])) - esi
        edx = ctypes.c_uint(edx).value

        edx = ctypes.c_uint(edx + ebx).value ^ ctypes.c_uint(esi >> 28).value ^ ctypes.c_uint(esi << 4).value
        esi = ctypes.c_uint(edi + esi).value
        edi = ctypes.c_uint(edi - edx).value ^ ctypes.c_uint(edx >> 26).value ^ ctypes.c_uint(edx << 6).value
        edx = ctypes.c_uint(esi + edx).value
        esi = ctypes.c_uint(esi - edi).value ^ ctypes.c_uint(edi >> 24).value ^ ctypes.c_uint(edi << 8).value
        edi = ctypes.c_uint(edx + edi).value
        ebx = ctypes.c_uint(edx - esi).value ^ ctypes.c_uint(esi >> 16).value ^ ctypes.c_uint(esi << 16).value
        esi = ctypes.c_uint(esi + edi).value
        edi = ctypes.c_uint(edi - ebx).value ^ ctypes.c_uint(ebx >> 13).value ^ ctypes.c_uint(ebx << 19).value
        ebx = ctypes.c_uint(ebx + esi).value
        esi = ctypes.c_uint(esi - edi).value ^ ctypes.c_uint(edi >> 28).value ^ ctypes.c_uint(edi << 4).value
        edi = ctypes.c_uint(edi + ebx).value
        i += 12

    if not (remaining := len(s) - i) > 0:
        return ctypes.c_ulong(esi << 32 | eax).value

    if remaining >= 12:
        esi = ctypes.c_uint(esi + (ord(s[i + 11]) << 24)).value

    if remaining >= 11:
        esi = ctypes.c_uint(esi + (ord(s[i + 10]) << 16)).value

    if remaining >= 10:
        esi = ctypes.c_uint(esi + (ord(s[i + 9]) << 8)).value

    if remaining >= 9:
        esi = ctypes.c_uint(esi + ord(s[i + 8])).value

    if remaining >= 8:
        edi = ctypes.c_uint(edi + (ord(s[i + 7]) << 24)).value

    if remaining >= 7:
        edi = ctypes.c_uint(edi + (ord(s[i + 6]) << 16)).value

    if remaining >= 6:
        edi = ctypes.c_uint(edi + (ord(s[i + 5]) << 8)).value

    if remaining >= 5:
        edi = ctypes.c_uint(edi + ord(s[i + 4])).value

    if remaining >= 4:
        ebx = ctypes.c_uint(ebx + (ord(s[i + 3]) << 24)).value

    if remaining >= 3:
        ebx = ctypes.c_uint(ebx + (ord(s[i + 2]) << 16)).value

    if remaining >= 2:
        ebx = ctypes.c_uint(ebx + (ord(s[i + 1]) << 8)).value

    if remaining >= 1:
        ebx = ctypes.c_uint(ebx + ord(s[i])).value

    esi = ctypes.c_uint((esi ^ edi) - ((edi >> 18) ^ (edi << 14))).value
    ecx = ctypes.c_uint((esi ^ ebx) - ((esi >> 21) ^ (esi << 11))).value
    edi = ctypes.c_uint((edi ^ ecx) - ((ecx >> 7) ^ (ecx << 25))).value
    esi = ctypes.c_uint((esi ^ edi) - ((edi >> 16) ^ (edi << 16))).value
    edx = ctypes.c_uint((esi ^ ecx) - ((esi >> 28) ^ (esi << 4))).value
    edi = ctypes.c_uint((edi ^ edx) - ((edx >> 18) ^ (edx << 14))).value
    eax = ctypes.c_uint((esi ^ edi) - ((edi >> 8) ^ (edi << 24))).value

    return ctypes.c_ulong((edi << 32) | eax).value
