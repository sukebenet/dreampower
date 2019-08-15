from multiprocessing.pool import ThreadPool

from config import Config as conf
from processing import Process
from utils import read_image, write_image


class SimpleImageTransform(Process):
    """
    Simple Image Processing Class
    """

    def __init__(self, input_path, phases, output_path):
        """
        ProcessImage Constructor
        :param input_path: <string> image path to process
        :param output_path: <string> image path to write the result.
        :param phases: <ImageTransform[]> list of transformation each image
        """
        super().__init__()
        self.__phases = phases
        self.__input_path = input_path
        self.__output_path = output_path
        self.__image_steps = []

    def info_start_run(self):
        super().info_start_run()
        conf.log.debug("Processing on {}".format(self.__input_path))

    def setup(self):
        self.__image_steps.append(read_image(self.__input_path))

    def execute(self):
        """
        Execute all phases on the image
        :return: None
        """

        for p in self.__phases:
            self.__image_steps.append(p.run(*[self.__image_steps[i] for i in p.input_index]))

        write_image(self.__image_steps[-1], self.__output_path)
        conf.log.debug("{} Image Created ".format(self.__output_path))

        return self.__image_steps[-1]


class MultipleImageTransform(Process):
    """
    Multiple Image Processing Class
    """

    def __init__(self, input_paths, phases, output_paths, children_process=SimpleImageTransform):
        """
        ProcessMultipleImages Constructor
        :param input_paths: <string[]> images path list to process
        :param output_paths: <string> images path to write the result
        :param children_process: <ImageTransform> Process to use on the list of input
        :param phases: <ImageTransform[]> list of transformation use by the process each image
        """
        super().__init__()
        self.__phases = phases
        self.__input_paths = input_paths
        self.__output_paths = output_paths
        self.__process_list = []
        self.__multiprocessing = conf.multiprocessing()
        self.__children_process = children_process

    def setup(self):
        self.__process_list = [self.__children_process(i[0], self.__phases, i[1])
                               for i in zip(self.__input_paths, self.__output_paths)]

    def execute(self):
        """
        Execute all phases on the list of images
        :return: None
        """

        def process_one_image(a):
            conf.log.info("Processing image : {}/{}".format(a[1] + 1, len(self.__process_list)))
            a[0].run()

        if not self.__multiprocessing:
            for x in zip(self.__process_list, range(len(self.__process_list))):
                process_one_image(x)
        else:
            conf.log.debug("Using Multiprocessing")
            pool = ThreadPool(conf.args['n_cores'])
            pool.map(process_one_image, zip(self.__process_list, range(len(self.__process_list))))
            pool.close()
            pool.join()