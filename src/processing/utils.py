import os

from config import Config as Conf
from utils import check_shape
from transform.gan.mask import CorrectToMask, MaskrefToMaskdet, MaskfinToNude
from transform.opencv.correct import DressToCorrect, ColorTransfer
from transform.opencv.mask import MaskToMaskref, MaskdetToMaskfin
from transform.opencv.resize import ImageToResized, ImageToCrop, ImageToOverlay, ImageToResizedCrop, ImageToRescale, ImageToNearest, ImageCompress


def shift_step(args, p, reason, shift_start_add=0, shift_end_add=0):
    #if not args['steps']:
    #    args['steps'] = (0, 5)

    if not args['steps']:
      return

    if args['steps'][1] != (len(p) - 1):
      shift_end_add = shift_start_add

    if args['steps'][0] == 0:
      shift_start_add = 0

    Conf.log.spam("Start: {} + {} = {} ({})".format(args['steps'][0], shift_start_add, args['steps'][0] + shift_start_add, reason))

    Conf.log.spam("End: {} + {} = {} ({})".format(args['steps'][1], shift_end_add, args['steps'][1] + shift_end_add, reason))

    args['steps'] = (
        args['steps'][0] + shift_start_add,
        args['steps'][1] + shift_end_add
    )


def shift_starting(args):
    if args.get('steps') and args['steps'][0] != 0:
        shift_step(args, shift_start_add=1)


def shift_ending(args, p):
    if args.get('steps') and args['steps'][1] < len(p):
        shift_step(args, shift_end_add=1)


def add_tail(args, p, add):
    p = [add] + p
    shift_step(args, p, add, shift_start_add=1,shift_end_add=1)
    #shift_starting(args)
    #shift_ending(args, p)
    return p


def add_head(args, p, add):
    p = p + [add]
    shift_step(args, p, add, shift_end_add=1)
    #shift_ending(args, p)
    return p


def overlay(args, p):
    p = add_tail(args, p, ImageToResized)
    p = add_tail(args, p, ImageToCrop)
    p = add_head(args, p, ImageToOverlay)
    return p


def auto_resize(args, p):
    return add_tail(args, p, ImageToResized)


def auto_resize_crop(args, p):
    return add_tail(args, p, ImageToResizedCrop)


def auto_rescale(args, p):
    return add_tail(args, p, ImageToRescale)

def auto_nearest(args, p):
    return add_tail(args, p, ImageToNearest)


def is_file(args, path):
    if not os.path.isfile(path):
        return False

    for mod in (overlay, auto_resize, auto_resize_crop, auto_rescale):
        if args.get(mod.__name__):
            return True

    if not args['ignore_size']:
        check_shape(path)
    else:
        Conf.log.warn('Image Size Requirements Unchecked.')
    return True


def scale_mod(args, p):
    for mod in (overlay, auto_resize, auto_resize_crop, auto_rescale):
        if args.get(mod.__name__):
            return mod(args, p)

    if os.path.isfile(Conf.args["input"]):
        is_file(args, Conf.args["input"])

    return auto_nearest(args, p)
    #return p


def select_phases(args):
    """
    Select the transformation phases to use following args parameters.

    :return: <ImageTransform[]> list of image transformation
    """

    phases = [DressToCorrect, CorrectToMask, MaskToMaskref,
              MaskrefToMaskdet, MaskdetToMaskfin, MaskfinToNude]

    phases = scale_mod(args, phases)

    if args['experimental_color_transfer']:
        phases = add_head(args, phases, ColorTransfer)

    if args['compress'] and args['compress'] > 0:
      phases = add_tail(args, phases, ImageCompress)

    return phases
