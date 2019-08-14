import time

from config import Config as conf
from utils import camel_case_to_str


class Process:
    """
    Abstract Process Class
    """

    def __init__(self):
        self.__start = time.time()

    def run(self):
        self.info_start_run()
        self.setup()
        self.execute()
        self.clean()
        self.info_end_run()

    def info_start_run(self):
        self.__start = time.time()
        conf.log.info("Executing {}".format(camel_case_to_str(self.__class__.__name__)))

    def info_end_run(self):
        conf.log.info("{} Finish".format(camel_case_to_str(self.__class__.__name__)))
        conf.log.debug("{} Done in {} seconds".format(
            camel_case_to_str(self.__class__.__name__), round(time.time() - self.__start, 2)))

    def setup(self):
        pass

    def execute(self):
        pass

    def clean(self):
        pass

    def __str__(self):
        return str(self.__class__.__name__)