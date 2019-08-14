"""
Image Transformation
"""
import time

from config import Config as conf
from utils import camel_case_to_str


class ImageTransform:
    """
    Abstract Image Transformation Class
    """

    def __init__(self, input_index=(-1,)):
        """
        Image Transformation Class Constructor
        :param input_index: index where to take the input (default is -1 for previous transformation)
        """
        self.__start = time.time()
        self.input_index = input_index

    def run(self, *args):
        self.__start = time.time()
        self.info_start_run()
        self.setup(*args)
        r = self.execute(*args)
        self.clean(*args)
        self.info_end_run()
        return r

    def info_start_run(self):
        self.__start = time.time()
        conf.log.info("Executing {}".format(camel_case_to_str(self.__class__.__name__)))

    def info_end_run(self):
        conf.log.debug("{} Done in {} seconds".format(
            camel_case_to_str(self.__class__.__name__), round(time.time() - self.__start, 2)))

    def setup(self, *args):
        pass

    def execute(self, *args):
        pass

    def clean(self, *args):
        pass