"""Prepares the data for object detection, using TensorFlow Object detection. Following : https://medium.freecodecamp.org/tracking-the-millenium-falcon-with-tensorflow-c8c86419225e
"""
import os
import os.path as op
from glob import glob
import magic
import shutil
from PIL import Image
from lxml import etree
parser = etree.HTMLParser()

from img_functions import img_max_sideresize

# Variables
xml_head_template = """
<annotation>
    <folder>{foldername}</folder>
    <filename>{filename}</filename>
    <size>
        <width>{width}</width>
        <height>{height}</height>
    </size>
    <segmented>0</segmented>
    {objects}
</annotation>
"""

xml_object_template = """
    <object>
        <name>{label}</name>
        <bndbox>
            <xmin>{xmin}</xmin>
            <ymin>{ymin}</ymin>
            <xmax>{xmax}</xmax>
            <ymax>{ymax}</ymax>
        </bndbox>
    </object>
"""


def get_labelling_commands(to_label_img_paths, predefined_classes_txt_path):
    """ Utility for outputing all commands to be sent to the labelling utility ! Don't forget to save the files under the annotation folder
    :param to_label_img_paths: list of img files to label
    :return:
    """
    print("Don't forget to : pip install labelImg (if necessary)")
    for img_path in to_label_img_paths:
        cmd = 'labelImg "{img_path}" "{predefined_classes_txt}"'.format(img_path=img_path,
                                                                        predefined_classes_txt=predefined_classes_txt_path)
        print(cmd)
    print("Don't forget to : pip install labelImg (if necessary)")


def create_obj_detection_training_data(orig_yolo_xmls_folder, orig_imgs_folder, train_folder, img_resize_max_length=None):
    """Prepares the data for object detection, using TensorFlow Object detection.
    Following : https://medium.freecodecamp.org/tracking-the-millenium-falcon-with-tensorflow-c8c86419225e
    Takes an empty "train_folder" and parameters everything as it should be for TensorFlow Object Detection.
    WARNING ! the 'link' between the images and xml is their names : XXX.jpg <=> XXX.xml, YYY.jpg <=> YYY.xml
    :param orig_yolo_xmls_folder: the original labelled xmls with labelImg (in Yolo mode)
    :param orig_imgs_folder: original images
    :param train_folder: the folder that should exists and that will be populated
    :param img_resize_max_length:
    :return:
    """
    assert op.exists(train_folder)

    train_imgs_folder = op.join(train_folder, 'train_images')
    annotations_folder = op.join(train_folder, 'annotations')
    train_xmls_folder = op.join(annotations_folder, 'xmls')
    os.makedirs(train_xmls_folder, exist_ok=True)
    os.makedirs(train_imgs_folder, exist_ok=True)
    os.makedirs(annotations_folder, exist_ok=True)
    trainval_txt_path = op.join(annotations_folder, "trainval.txt")
    labelmap_txt_path = op.join(annotations_folder, "label_map.pbtxt")
    items = set()

    # Create training db
    trainval_txt = ''
    for ix1, orig_img_path in enumerate(glob(op.join(orig_imgs_folder, '*'), recursive=True)):
        # Gen paths
        xml_path = op.join(train_xmls_folder, op.splitext(op.basename(orig_img_path))[0] + '.xml')
        orig_xml_path = op.join(orig_yolo_xmls_folder, op.splitext(op.basename(orig_img_path))[0] + '.xml')
        img_path = op.join(train_imgs_folder, op.splitext(op.basename(orig_img_path))[0] + '.jpg')

        # Exclude some images
        if "image" not in magic.from_file(orig_img_path, mime=True):
            continue
        if not op.exists(orig_xml_path):
            continue

        # # Copy image + reduce as jpg
        rgb_im = Image.open(orig_img_path).convert('RGB')
        # if img_resize_max_length: # TODO
        #     rgb_im = img_max_sideresize(rgb_im, img_resize_max_length)
        rgb_im.save(img_path)

        # Copy xml
        shutil.copy(orig_xml_path, xml_path)

        tree = etree.parse(open(orig_xml_path), parser=parser)
        items = items.union(set(tree.xpath('//object//name//text()')))

        # Adding to trainval_txt
        trainval_txt += op.splitext(op.basename(img_path))[0] + '\n'

    # Create trainval.txt
    with open(trainval_txt_path, 'w') as f:
        f.write(trainval_txt)

    # Create labelmap_txt_path
    item_mask = """item {
  id: {count}
  name: '{name}'
}"""

    labelmap_txt = ''
    for ix, k in enumerate(items):
        labelmap_txt += item_mask.replace('{count}', str(ix+1)).replace("{name}", k) + '\n'

    with open(labelmap_txt_path, 'w') as f:
        f.write(labelmap_txt)


def handle_obj_detection_model_and_config_faster_rcnn_resnet101(train_folder, orig_model_ckpt, min_dimension, max_dimension,
                                                                config_dest_path, floyd=False):

    # Handle Model
    model_folder = op.join(train_folder, 'model')
    os.makedirs(model_folder, exist_ok=True)
    for model_file_p in glob(op.join(orig_model_ckpt, 'model.ckpt.*')):
        dest_model_file_p = op.join(model_folder, op.basename(model_file_p))
        shutil.copy(model_file_p, dest_model_file_p)

    # Handle config file
    mask_config = 'ressources/faster_rcnn_resnet101.config'
    with open(mask_config, 'r') as f:
        config_str = f.read()

    with open(op.join(train_folder, 'annotations', 'label_map.pbtxt'), 'r') as f:
        labelmap_txt = f.read()

    config_str = config_str.replace('{NB_CLASSES}', str(labelmap_txt.count('id:')))
    config_str = config_str.replace('{MIN_DIMENSION}', str(min_dimension))
    config_str = config_str.replace('{MAX_DIMENSION}', str(max_dimension))
    config_str = config_str.replace('{MODEL_CKPT_PATH}', op.join('/input/model' if floyd else model_folder, 'model.ckpt'))
    assert op.exists(op.join(train_folder, 'train.record'))
    assert op.exists(op.join(train_folder, 'val.record'))
    config_str = config_str.replace('{TRAIN_RECORD}', op.join('/input' if floyd else train_folder, 'train.record'))
    config_str = config_str.replace('{VAL_RECORD}', op.join('/input' if floyd else train_folder, 'val.record'))
    config_str = config_str.replace('{LABELMAP_TXT_PATH}', op.join('/input' if floyd else train_folder, 'annotations', 'label_map.pbtxt'))

    with open(config_dest_path, 'w') as f:
        f.write(config_str)



def gen_xml_file():
    """Maybe useful cde"""
    pass
    # Unsused for now
    # # Gen XML head
    # with Image.open(img_path) as img_f:
    #     width, height = img_f.size
    #
    # objects_str = ''
    #
    # # Gen bboxes
    # for ix2, row in df.iterrows():
    #     if row['label'] in ['caption', 'table', 'signature']:
    #         objects_str += xml_object_template.format(label=row['label'],
    #                                                   xmin=int(wpercent*row['xmin'] + 0.5), ymin=int(wpercent*row['ymin'] + 0.5),
    #                                                   xmax=int(wpercent*row['xmax'] + 0.5), ymax=int(wpercent*row['ymax'] + 0.5))
    #
    # # Copy files and add proper informations
    # xml = xml_head_template.format(foldername=op.dirname(img_path).split('/')[-1], filename=op.basename(img_path),
    #                                width=width, height=height, objects=objects_str)
    #
    # # Create XML file
    # with open(xml_path, 'w') as f:
    #     f.write(xml)


if __name__ == '__main__':
    img_paths = glob("/data/datascience/innovafeed/images/*")
    get_labelling_commands(img_paths, "/data/datascience/innovafeed/annotations/predefined_classes.txt")
    orig_yolo_xmls_folder = "/data/datascience/innovafeed/annotations/xmls_yolo"
    orig_imgs_folder = "/data/datascience/innovafeed/images"
    train_folder = "/data/datascience/innovafeed/train_data"
    create_obj_detection_training_data(orig_yolo_xmls_folder, orig_imgs_folder, train_folder)
    orig_model_ckpt = "/code/ml/models_zoo/faster_rcnn_resnet101_coco_11_06_2017"

    # Home config
    config_dest_path = "/code/ml/tutorials/floyd_tests/worm_detect/faster_rcnn_resnet101_home.config"
    handle_obj_detection_model_and_config_faster_rcnn_resnet101(train_folder, orig_model_ckpt, 400, 600, config_dest_path)

    # Floyd config
    config_dest_path = "/code/ml/tutorials/floyd_tests/worm_detect/faster_rcnn_resnet101_floyd.config"
    handle_obj_detection_model_and_config_faster_rcnn_resnet101(train_folder, orig_model_ckpt, 2500, 4000, config_dest_path, floyd=True)
