""" Wokers definition """
# TODO Implement this with a queue and mutliprocessing
import inspect

from transform.gan.mask import CorrectToMask, MaskrefToMaskdet, MaskfinToNude
from transform.opencv.correct import DressToCorrect, ColorTransfer
from transform.opencv.mask import MaskToMaskref, MaskdetToMaskfin
from transform.opencv.resize import ImageToResized, ImageToCrop, ImageToOverlay, ImageToResizedCrop, ImageToRescale

workers = {
    "DressToCorrect": DressToCorrect,
    "CorrectToMask": CorrectToMask,
    "MaskToMaskref": MaskToMaskref,
    "MaskrefToMaskdet": MaskrefToMaskdet,
    "MaskdetToMaskfin": MaskdetToMaskfin,
    "MaskfinToNude": MaskfinToNude,
    "ImageToResized": ImageToResized,
    "ImageToCrop": ImageToCrop,
    "ImageToOverlay": ImageToOverlay,
    "ImageToResizedCrop": ImageToResizedCrop,
    "ImageToRescale": ImageToRescale,
    "ColorTransfer": ColorTransfer
}


def get_worker(name):
    w = workers.get(name)
    if inspect.isclass(w):
        w = w()
        workers[name] = w
    return w
