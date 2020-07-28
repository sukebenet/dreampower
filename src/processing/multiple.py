"""Multiple Image Transform Processing."""
import copy
from multiprocessing.pool import ThreadPool

from config import Config as Conf
from processing import Processing, SimpleProcessing
from utils import camel_case_to_str


class MultipleImageProcessing(Processing):
    """Multiple Image Processing Class."""
    def _setup(self, *args):
        self._input_paths = self._args['input']
        self._output_paths = self._args['output']
        self._process_list = []
        self._multiprocessing = Conf.multiprocessing()

        self._process_list = []

        for input_path, output_path in zip(self._input_paths, self._output_paths):
            args = copy.deepcopy(self._args)
            args['input'] = input_path
            args['output'] = output_path
            self._process_list.append((SimpleProcessing(args), args))
        #Conf.log.debug(self._process_list)

    def _process_one(self, a):
        Conf.log.info("{} : {}/{}".format(
            camel_case_to_str(self.__class__.__name__), a[1] + 1, len(self._process_list)
        ))
        a[0][0].run(config=a[0][1])

    def _execute(self, *args):
        """
        Execute all phases on the list of images.

        :return: None
        """
        if not self._multiprocessing:
            for x in zip(self._process_list, range(len(self._process_list))):
                self._process_one(x)

        else:
            Conf.log.debug("Using Multiprocessing")
            pool = ThreadPool(Conf.cores())
            pool.map(self._process_one, zip(self._process_list, range(len(self._process_list))))
            pool.close()
            pool.join()
