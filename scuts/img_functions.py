import os.path as op
import numpy as np
from PIL import Image, ImageDraw
import magic
import imageio
import time as tm
import cv2


# Functions
def color_img(img, mode='BGR', channel=None):
    """Takes a cv2 image as input and changes its color mode
    :param img: BGR or GRAY img only
    :param mode: BGR, RGB, GRAY, HSV
    :param channel: specific channel to be extracted
    """
    img = img.astype(np.uint8)
    nb_channels = len(img.shape)

    if nb_channels == 2:
        if (mode == 'BGR' or mode == 'RGB'):
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)  # BGR or RGB identical
        if mode == 'HSV':
            print('Warning: conversion to GRAY to HSV space')
    else:
        if mode == 'RGB':
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        if mode == 'HSV':
            img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        if mode == 'GRAY':
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    if type(channel) != type(None): img = cv2.split(img)[channel]
    return (img)


def show_img(img, title=None):
    """
    :return: display an image with PIL
    """
    img = Image.fromarray(np.uint8(img))
    if title:
        draw = ImageDraw.Draw(img)
        draw.text((1, 1), str(title), 255)
        draw.text((1, 10), str(title), 0)
        img.show()
    else:
        img.show()
    tm.sleep(0.2)


def cv2_imread(img_path):
    if magic.from_file(img_path, mime=True) == 'image/gif':
        img = imageio.mimread(img_path)[0]
        if len(img.shape) == 3:
            img_4channel = cv2.cvtColor(img, cv2.COLOR_RGB2RGBA)
        else:
            img_4channel = cv2.cvtColor(img, cv2.COLOR_GRAY2RGBA)
    else:
        img_4channel = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
        img_4channel = cv2.cvtColor(img_4channel, cv2.COLOR_BGRA2RGBA)
    alpha_channel = img_4channel[:, :, 3]
    rgb_channels = img_4channel[:, :, :3]

    # White Background image
    white_background_img = np.ones_like(rgb_channels, dtype=np.uint8) * 255

    # Alpha factor
    alpha_factor = alpha_channel[:, :, np.newaxis].astype(np.float32) / 255.0
    alpha_factor = np.concatenate((alpha_factor, alpha_factor, alpha_factor), axis=2)

    # Transparent image Rendered on white Background
    base = rgb_channels.astype(np.float32) * alpha_factor
    white = white_background_img.astype(np.float32) * (1 - alpha_factor)
    img_final = base + white
    return img_final.astype(np.uint8)


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
