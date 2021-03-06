import os
from os.path import dirname
import h5py
import numpy as np

PASCAL_CLASSES = ['aeroplane', 'bicycle', 'boat', 'bottle', 'bus', 'car',
                  'chair', 'diningtable', 'motorbike', 'sofa',  'train', 'tvmonitor']


def help():
    print("File %s not found!\n\n"
          "Download the preprocessed PASCAL3D+ dataset first:\n\n"
          "https://drive.google.com/open?id=1bDcISYXmCcTqZhhCX-bhTuUCmEH1Q8YF\n\n")


def train_val_split(x, y, val_split=0.2, canonical_split=True):

    if canonical_split:
        val_split = 0.2
        np.random.seed(13)

    n_samples = x.shape[0]

    shuffled_samples = np.random.choice(n_samples, n_samples, replace=False)

    n_train = int((1-val_split)*n_samples)
    train_samples = shuffled_samples[0:n_train]
    val_samples = shuffled_samples[n_train:]

    x_train, y_train = x[train_samples], y[train_samples]
    x_val, y_val = x[val_samples], y[val_samples]

    np.random.seed(None)

    return x_train, y_train, x_val, y_val


def get_class_data(data_h5, cls_name):

    images = np.asarray(data_h5[cls_name]['images'])
    azimuth_bit = np.asarray(data_h5[cls_name]['azimuth_bit'])
    elevation_bit = np.asarray(data_h5[cls_name]['elevation_bit'])
    tilt_bit = np.asarray(data_h5[cls_name]['tilt_bit'])
    angles = np.hstack([azimuth_bit, elevation_bit, tilt_bit])

    return images, angles


def merge_all_classes(data):

    images = []
    angles = []
    for cls_key in data.keys():
        cls_images, cls_angles = get_class_data(data, cls_key)
        images.append(cls_images)
        angles.append(cls_angles)

    images = np.vstack(images)
    angles = np.vstack(angles)

    return images, angles


def load_pascal_data(pascaldb_path, cls=None, val_split=0.2, canonical_split=True):
    """ Load cropped ground truth images from PASCAL3D+ dataset (augmented with Imagenet)

    Original data:
        http://cvgl.stanford.edu/projects/pascal3d.html

    The following repository was also used to create dataset:
        https://github.com/ShapeNet/RenderForCNN

    Parameters
    ----------
    cls: str
        PASCAL object class to load (see PASCAL_CLASSES for available options). If None, all classes will be loaded.
    val_split: float
        amount of data used for validation
    canonical_split: bool
        whether to fix a random seed used for validation

    Returns
    -------

    x_train: numpy array of shape [n_images, 224, 224, 3]
        train cropped object images
    y_train: numpy array of shape [n_images, 6]
        train ground truth object orientation utils (pan-tilt-roll) in biternion form:
        [pan_cos, pan_sin, tilt_cos, tilt_sin, roll_cos, roll_sin]
    x_val: numpy array of shape [n_images, 224, 224, 3]
        validation images
    y_val: numpy array of shape [n_images, 6]
        validation ground truth utils
    x_test: numpy array of shape [n_images, 224, 224, 3]
        test images
    y_test: numpy array of shape [n_images, 6]
        test ground truth utils

    """

    if not os.path.exists(pascaldb_path):
        help()

    train_test_data_db = h5py.File(pascaldb_path, 'r')

    train_data = train_test_data_db['train']
    test_data = train_test_data_db['test']

    if cls is None:
        x_train, y_train = merge_all_classes(train_data)
        x_test, y_test = merge_all_classes(test_data)
    else:
        x_train, y_train = get_class_data(train_data, cls)
        x_test, y_test = get_class_data(test_data, cls)

    x_train, y_train, x_val, y_val = train_val_split(x_train, y_train,
                                                     val_split=val_split,
                                                     canonical_split=canonical_split)

    return x_train, y_train, x_val, y_val, x_test, y_test
