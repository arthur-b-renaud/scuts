import os.path as op
from scuts.img_functions import img_max_sideresize
from PIL import Image


def test_img_max_sideresize():
    img_test_path = op.join(op.dirname(__file__), 'test_ressources/img_test.png')
    img = Image.open(img_test_path)
    img = img_max_sideresize(img, 200)
    assert img.size[0] == 200

