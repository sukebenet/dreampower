"""Images Transforms."""
import time

from config import Config as Conf
from utils import camel_case_to_str


class ImageTransform:
    """Abstract Image Transformation Class."""

    def __init__(self, input_index=(-1,), args=None):
        """
        Image Transformation Class Constructor.

        :param input_index: <tuple> index where to take the inputs (default is (-1) for previous transformation)
        :param args: <dict> args parameter to run the image transformation (default use Conf.args)
        """
        self.__start = time.time()
        self.input_index = input_index
        self._args = Conf.args.copy() if args is None else args.copy()

    def run(self, *args):
        """
        Run the Image Transform.

        :param args: <dict> settings for the transformation
        :return: <RGB> image
        """
        self.__start = time.time()
        self.info_start_run()
        self._setup(*args)
        r = self._execute(*args)
        self._clean(*args)
        self.info_end_run()
        return r

    def info_start_run(self):
        """
        Log info at the start of the run.

        :return: None
        """
        self.__start = time.time()
        Conf.log.info("Executing {}".format(camel_case_to_str(self.__class__.__name__)))

    def info_end_run(self):
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
