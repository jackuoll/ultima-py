from settings import is_mount
from sdk.animations import *
from sdk.tile_data import item_data
from PIL import ImageChops


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
    bg = Image.new(im.mode, im.size, im.getpixel((0,0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)


def mount_info(layers):
    for item_id, hue in layers:
        if is_mount(item_id):
            return item_id, hue
    return None, None


def frame_of(female, body_hue, layers, order=True):
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
        mount_img = Animation.get_animation(mount, 2, 1, mount_hue, True)
        paste_centered(img, mount_img)
    player_frames = Animation.get_animation(401 if female else 400, action, 1, body_hue, True)

    paste_centered(img, player_frames)
    for item_id, hue in filter(lambda item_id, hue: not is_mount(item_id), layers):
        item = item_data(item_id)
        clothing_frame = Animation.get_animation(item.animation, action, 1, hue, True)
        if not clothing_frame:
            continue
        paste_centered(img, clothing_frame)
    return trim(img)
