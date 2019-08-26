"""Images Transforms."""
import time

from config import Config as Conf
from processing import Processing


class ImageTransform(Processing):
    """Abstract Image Transformation Class."""

    def __init__(self, input_index=(-1,), args=None):
        """
        Image Transformation Class Constructor.

        :param input_index: <tuple> index where to take the inputs (default is (-1) for previous transformation)
        :param args: <dict> args parameter to run the image transformation (default use Conf.args)
        """

        super().__init__(args)
        self.__start = time.time()
        self.input_index = input_index
        self._args = Conf.args.copy() if args is None else args.copy()
