"""Processing."""
import os
import time

from config import Config as Conf
from utils import camel_case_to_str, cv2_supported_extension, ffmpeg_supported_extension


class Processing:
    """ Abstract Processing Class """
    def run(self, *args, config=None):
        """
        Run the Image Transform.

        :param args: <dict> settings for the transformation
        :return: <RGB> image
        """
        self.running = True
        self._start = time.time()
        self._args = Conf.args.copy() if config is None else config.copy()
        self._info_start_run()
        self._setup(*args)
        r = self._execute(*args)
        self._clean(*args)
        self._info_end_run()
        self.running = False
        return r

    def _info_start_run(self):
        """
        Log info at the start of the run.

        :return: None
        """
        self.__start = time.time()
        Conf.log.spam("Executing {}".format(camel_case_to_str(self.__class__.__name__)))

    def _info_end_run(self):
        """
        Log info at the end of the run.

        :return: None
        """
        Conf.log.success("{} Done in {} seconds".format(
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
        ext = os.path.splitext(args['input'])[1]

        if ext == ".gif":
            from processing.gif import GifProcessing
            return GifProcessing()
        elif ext in ffmpeg_supported_extension():
            from processing.video import VideoProcessing
            return VideoProcessing()
        elif ext in cv2_supported_extension():
            from processing.image import ImageProcessing
            return ImageProcessing()
        else:
            return None
