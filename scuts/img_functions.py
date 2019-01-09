from PIL import Image


def img_max_sideresize(img, max_side_size):
    """Resizes image so that
    :param img: a PIL Image
    :param max_side_size:
    :return:
    """
    if img.size[0] > img.size[1]:
        wpercent = (max_side_size / float(img.size[0]))
        hsize = int((float(img.size[1]) * float(wpercent)))
        img = img.resize((max_side_size, hsize), Image.ANTIALIAS)
    else:
        hpercent = (max_side_size / float(img.size[1]))
        wsize = int((float(img.size[0]) * float(hpercent)))
        img = img.resize((wsize, max_side_size), Image.ANTIALIAS)
    return img
