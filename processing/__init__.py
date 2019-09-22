"""Processing."""
import os
import time

from config import Config as Conf
from utils import camel_case_to_str, cv2_supported_extension


class Processing:
    """ Abstract Processing Class """
    def __init__(self, args=None):
        """
        Image Processing Class Constructor.

        :param input_index: <tuple> index where to take the inputs (default is (-1) for previous transformation)
        :param args: <dict> args parameter to run the image transformation (default use Conf.args)
        """
        self.__start = time.time()
        self._args = Conf.args.copy() if args is None else args.copy()

    def run(self, *args):
        """
        Run the Image Transform.

        :param args: <dict> settings for the transformation
        :return: <RGB> image
        """
        self.__start = time.time()
        self._info_start_run()
        self._setup(*args)
        r = self._execute(*args)
        self._clean(*args)
        self._info_end_run()
        return r

    def _info_start_run(self):
        """
        Log info at the start of the run.

        :return: None
        """
        self.__start = time.time()
        Conf.log.info("Executing {}".format(camel_case_to_str(self.__class__.__name__)))

    def _info_end_run(self):
        """
        Log info at the end of the run.

        :return: None
        """
        Conf.log.debug("{} Done in {} seconds".format(
            camel_case_to_str(self.__class__.__name__), round(time.time() - self.__start, 2)))

    def _setup(self, *args):
        """
        Configure the transformation.

        :param args: <dict> settings for the transformation
        :return: None
        """
        pass

    def _execute(self, *args):
        """
        Execute the transformation.

        :param args: <dict> settings for the transformation
        :return: None
        """
        pass

    def _clean(self, *args):
        """
        Clean the transformation.

        :param args: <dict> settings for the transformation
        :return: None
        """
        pass


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
