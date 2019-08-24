"""Processing."""
import os
import time

from config import Config as Conf
from transform.gan.mask import CorrectToMask, MaskrefToMaskdet, MaskfinToNude
from transform.opencv.correct import DressToCorrect, ColorTransfer
from transform.opencv.mask import MaskToMaskref, MaskdetToMaskfin
from transform.opencv.resize import ImageToResized, ImageToCrop, ImageToOverlay, ImageToResizedCrop, ImageToRescale
from utils import camel_case_to_str, cv2_supported_extension, check_shape


class Processing:
    """Abstract Process Class."""

    def __init__(self, args=None):
        """
        Process Constructor.

        :param args: <dict> args parameter to run the image transformation (default use Conf.args)
        """
        self.__start = time.time()
        self._args = Conf.args.copy() if args is None else args.copy()

    def run(self):
        """
        Run the process.

        :return: None
        """
        self._info_start_run()
        self._setup()
        self._execute()
        self._clean()
        self._info_end_run()

    def _info_start_run(self):
        """
        Log info when the process run begin.

        :return: None
        """
        self.__start = time.time()
        Conf.log.info("Executing {}".format(camel_case_to_str(self.__class__.__name__)))

    def _info_end_run(self):
        """
        Log info when the process run end.

        :return: None
        """
        Conf.log.info("{} Finish".format(camel_case_to_str(self.__class__.__name__)))
        Conf.log.debug("{} Done in {} seconds".format(
            camel_case_to_str(self.__class__.__name__), round(time.time() - self.__start, 2)))

    def _setup(self):
        """
        Configure the process to be ready to execute.

        :return: None
        """
        pass

    def _execute(self):
        """
        Execute the process.

        :return: None
        """
        pass

    def _clean(self):
        """
        Cleanup a process execution.

        :return: None
        """


class SimpleProcessing(Processing):
    """Simple Transform Class."""

    def __init__(self, args=None):
        """
        Construct a Simple Processing .

        :param args: <dict> args parameter to run the image transformation (default use Conf.args)
        """
        super().__init__(args)

    def __new__(cls, args=None):
        """
        Create the correct SimpleTransform object corresponding to the input_path format.

        :param args: <dict> args parameter to run the image transformation (default use Conf.args)
        :return: <ImageProcessing|GiftProcessing|None> SimpleTransform object corresponding to the input_path format
        """
        args = Conf.args.copy() if args is None else args.copy()

        if os.path.splitext(args['input'])[1] == ".gif":
            from processing.gif import GifProcessing
            return GifProcessing(args=args)
        elif os.path.splitext(args['input'])[1] in cv2_supported_extension():
            from processing.image import ImageProcessing
            return ImageProcessing(args=args)
        else:
            return None


def select_phases(args):
    """
    Select the transformation phases to use following args parameters.

    :return: <ImageTransform[]> list of image transformation
    """
    def shift_step(shift_starting=0, shift_ending=0):
        if not args['steps']:
            args['steps'] = (0, 5)
        args['steps'] = (
            args['steps'][0] + shift_starting,
            args['steps'][1] + shift_ending
        )

    def add_tail(phases, phase):
        phases = [phase] + phases
        if args['steps'] and args['steps'][0] != 0:
            shift_step(shift_starting=1)
        if args['steps'] and args['steps'][1] == len(phases) - 1:
            shift_step(shift_ending=1)
        return phases

    def add_head(phases, phase):
        phases = phases + [phase]
        if args['steps'] and args['steps'][1] == len(phases) - 1:
            shift_step(shift_ending=1)
        return phases

    phases = [DressToCorrect, CorrectToMask, MaskToMaskref,
              MaskrefToMaskdet, MaskdetToMaskfin, MaskfinToNude]
    Conf.log.debug(args)
    if args['overlay']:
        phases = add_tail(phases, ImageToResized)
        phases = add_tail(phases, ImageToCrop)
        phases = add_head(phases, ImageToOverlay)
    elif args['auto_resize']:
        phases = add_tail(phases, ImageToResized)
    elif args['auto_resize_crop']:
        phases = add_tail(phases, ImageToResizedCrop)
    elif args['auto_rescale']:
        phases = add_tail(phases, ImageToRescale)
    elif os.path.isfile(args['input']):
        if not args['ignore_size']:
            check_shape(args['input'])
        else:
            Conf.log.warn('Image Size Requirements Unchecked.')

    if args['color_transfer']:
        phases = add_head(phases, ColorTransfer)

    return phases
