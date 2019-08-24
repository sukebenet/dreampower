"""Multiple Image Transform Processing."""
import copy
from multiprocessing.pool import ThreadPool

from config import Config as Conf
from processing import Processing, SimpleProcessing
from utils import camel_case_to_str


class MultipleImageProcessing(Processing):
    """Multiple Image Processing Class."""

    def __init__(self,  args=None, children_process=SimpleProcessing):
        """
        Process Multiple Images Constructor.

        :param children_process: <ImageTransform> Process to use on the list of input
        :param args:  args: <dict> args parameter to run images transformations (default use Conf.args)
        """
        super().__init__(args=args)
        self._input_paths = self._args['input']
        self._output_paths = self._args['output']
        self._process_list = []
        self.__multiprocessing = Conf.multiprocessing()
        self.__children_process = children_process

    def _setup(self):
        self._process_list = []

        for input_path, output_path in zip(self._input_paths, self._output_paths):
            args = copy.deepcopy(self._args)
            args['input'] = input_path
            args['output'] = output_path
            self._process_list.append(self.__children_process(args=args))

    def _execute(self):
        """
        Execute all phases on the list of images.

        :return: None
        """
        def process_one_image(a):
            Conf.log.info("{} : {}/{}".format(
                camel_case_to_str(self.__class__.__name__), a[1] + 1, len(self._process_list)
            ))
            a[0].run()

        if not self.__multiprocessing:
            for x in zip(self._process_list, range(len(self._process_list))):
                process_one_image(x)
        else:
            Conf.log.debug("Using Multiprocessing")
            pool = ThreadPool(Conf.args['n_cores'])
            pool.map(process_one_image, zip(self._process_list, range(len(self._process_list))))
            pool.close()
            pool.join()
