def readbyte(buf):
    """Should be removed."""
    return ord(buf.read(1))


def safe_list_get(list, idx, default):
    try:
        return list[idx]
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