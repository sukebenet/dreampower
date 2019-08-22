import json
import os
import pathlib
import shutil
import sys
import tempfile
import time
from json import JSONDecodeError
from multiprocessing.pool import ThreadPool

import cv2
import imageio

import argv
from config import Config as conf
from utils import camel_case_to_str, cv2_supported_extension, read_image, write_image, json_to_argv, check_shape


class Process:
    """
    Abstract Process Class

    """

    def __init__(self, *_args, args=None):
        """
        Process Constructor
        :param args: <dict> args parameter to run the image transformation (default use conf.args)
        """
        self.__start = time.time()
        self._args = conf.args.copy() if args is None else args.copy()

    def run(self):
        """
        Run the process
        :return: None
        """
        self._info_start_run()
        self._setup()
        self._execute()
        self._clean()
        self._info_end_run()

    def _info_start_run(self):
        """
        Logging when the process run begin
        :return: None
        """
        self.__start = time.time()
        conf.log.info("Executing {}".format(camel_case_to_str(self.__class__.__name__)))

    def _info_end_run(self):
        """
        Logging when the process run end
        :return: None
        """
        conf.log.info("{} Finish".format(camel_case_to_str(self.__class__.__name__)))
        conf.log.debug("{} Done in {} seconds".format(
            camel_case_to_str(self.__class__.__name__), round(time.time() - self.__start, 2)))

    def _setup(self):
        """
        Setup the process to be ready to execute
        :return: None
        """
        pass

    def _execute(self):
        """
        Execute the process
        :return: None
        """
        pass

    def _clean(self):
        """
        Cleanup a process execution
        :return: None
        """

    def __str__(self):
        return str(self.__class__.__name__)


class SimpleTransform(Process):
    """
    Simple Transform Class
    """

    def __init__(self, input_path, phases, output_path, args):
        super().__init__(input_path, phases, output_path, args)

    def __new__(cls, input_path, phases, output_path, args=None):
        """
        Create the correct SimpleTransform object (ImageTransform or GiftTransform) corresponding to the input_path format
        :param input_path: <string> original image path to process
        :param output_path: <string> image path to write the result.
        :param phases: <ImageTransform[]> list of Class transformation each image
        :param args: <dict> args parameter to run the image transformation (default use conf.args)
        :return: <ImageTransform|GiftTransform|None> SimpleTransform object corresponding to the input_path format
        """
        if os.path.splitext(input_path)[1] == ".gif":
            return GifTransform(input_path, phases, output_path, args=args)
        elif os.path.splitext(input_path)[1] in cv2_supported_extension():
            return ImageTransform(input_path, phases, output_path, args=args)
        else:
            return None


class ImageTransform(Process):
    """
    Image Processing Class
    """

    def __init__(self, input_path, phases, output_path, args=None):
        """
        ProcessImage Constructor
        :param input_path: <string> original image path to process
        :param output_path: <string> image path to write the result.
        :param args: <dict> args parameter to run the image transformation (default use conf.args)
        :param phases: <ImageTransform[]> list Class of transformation each image
        """
        super().__init__(args=args)
        self.__phases = phases
        self.__output_path = output_path
        self.__altered_path = self._args['altered']
        self.__starting_step = self._args['steps'][0] if self._args['steps'] else 0
        self.__ending_step = self._args['steps'][1] if self._args['steps'] else None

        if not conf.args['ignore_size']:
            check_shape(read_image(input_path))
        else:
            conf.log.warn('Image Size Requirements Unchecked.')

        conf.log.debug("All Phases : {}".format(self.__phases))
        conf.log.debug("To Be Executed Phases : {}".format(self.__phases[self.__starting_step:self.__ending_step]))

        path = self.__altered_path if os.path.isfile(self._args['input']) or not self._args.get('folder_altered')  \
            else os.path.join(self._args['folder_altered'], os.path.basename(self.__output_path))

        self.__image_steps = [input_path] + [
            os.path.join(path, "{}.png".format(p().__class__.__name__))
            for p in self.__phases[:self.__starting_step]
        ]
        conf.log.debug(self.__image_steps)

    def _info_start_run(self):
        super()._info_start_run()
        conf.log.info("Processing on {}".format(str(self.__image_steps)[2:-2]))

    def _setup(self):
        try:
            self.__image_steps = [read_image(x) if isinstance(x, str) else x for x in self.__image_steps]
        except FileNotFoundError as e:
            conf.log.error(e)
            conf.log.error("{} is not able to resume because it not able to load required images. "
                           .format(camel_case_to_str(self.__class__.__name__)))
            conf.log.error("Possible source of this error is that --altered argument is not a correct "
                           "directory path that contains valid images.")
            sys.exit(1)

    def _execute(self):
        """
        Execute all phases on the image
        :return: None
        """
        for p in (x(args=self._args) for x in self.__phases[self.__starting_step:self.__ending_step]):
            r = p.run(*[self.__image_steps[i] for i in p.input_index])
            self.__image_steps.append(r)

            if self.__altered_path:
                path = self.__altered_path \
                    if os.path.isfile(self._args['input']) or not self._args.get('folder_altered') \
                    else os.path.join(self._args['folder_altered'], os.path.basename(self.__output_path))

                write_image(r, os.path.join(path, "{}.png".format(p.__class__.__name__)))

                conf.log.debug("{} Step Image Of {} Execution".format(
                    os.path.join(path, "{}.png".format(p.__class__.__name__)),
                    camel_case_to_str(p.__class__.__name__),
                ))

        write_image(self.__image_steps[-1], self.__output_path)
        conf.log.info("{} Created".format(self.__output_path))
        conf.log.debug("{} Result Image Of {} Execution"
                       .format(self.__output_path, camel_case_to_str(self.__class__.__name__)))

        return self.__image_steps[-1]


class MultipleImageTransform(Process):
    """
    Multiple Image Processing Class
    """

    def __init__(self, input_paths, phases, output_paths, children_process=SimpleTransform, args=None):
        """
        ProcessMultipleImages Constructor
        :param input_paths: <string[]> images path list to process
        :param output_paths: <string> images path to write the result
        :param children_process: <ImageTransform> Process to use on the list of input
        :param phases: <ImageTransform[]> list of Class transformation use by the process each image
        """
        super().__init__(args=args)
        self._phases = phases
        self._input_paths = input_paths
        self._output_paths = output_paths
        self._process_list = []
        self.__multiprocessing = conf.multiprocessing()
        self.__children_process = children_process

    def _setup(self):
        self._process_list = [self.__children_process(i[0], self._phases, i[1], args=self._args)
                              for i in zip(self._input_paths, self._output_paths)]

    def _execute(self):
        """
        Execute all phases on the list of images
        :return: None
        """

        def process_one_image(a):
            conf.log.info("Processing Image : {}/{}".format(a[1] + 1, len(self._process_list)))
            a[0].run()

        if not self.__multiprocessing:
            for x in zip(self._process_list, range(len(self._process_list))):
                process_one_image(x)
        else:
            conf.log.debug("Using Multiprocessing")
            pool = ThreadPool(conf.args['n_cores'])
            pool.map(process_one_image, zip(self._process_list, range(len(self._process_list))))
            pool.close()
            pool.join()


class FolderImageTransform(MultipleImageTransform):
    """
    Folder Image Processing Class
    """

    def __init__(self, input_folder_path, phases, output_folder_path, args=None):
        """
        FolderImageTransform Constructor
        """
        super().__init__([], phases, [], args=args)
        self.__input_folder_path = input_folder_path
        self.__output_folder_path = output_folder_path
        self.__multiprocessing = conf.multiprocessing()

    def _setup(self):
        conf.log.debug([(r, d, f) for r, d, f in os.walk(self.__input_folder_path)])
        self._process_list = [
            MultipleImageTransform(
                [
                    x.path for x in os.scandir(r)
                    if x.is_file() and os.path.splitext(x.path)[1] in cv2_supported_extension() + [".gif"]
                ],
                self._phases,
                [
                    "{}{}{}".format(
                        os.path.splitext(x.path)[0],
                        '_out',
                        os.path.splitext(x.path)[1]
                    )
                    if not conf.args['output'] else
                    os.path.join(
                        conf.args['output'],
                        pathlib.Path(*pathlib.Path(r).parts[1:]),
                        os.path.basename(x.path)
                    )
                    for x in os.scandir(r)
                    if x.is_file() and os.path.splitext(x.path)[1] in cv2_supported_extension() + [".gif"]
                ],
                args=self.__get_folder_args(r)
            ) for r, _, _ in os.walk(self.__input_folder_path)
        ]

    def __get_folder_args(self, folder_path):
        def add_folder_altered(args):
            if args['altered']:
                args['folder_altered'] = os.path.join(args['altered'],
                                                      pathlib.Path(*pathlib.Path(folder_path).parts[1:]))
            return args

        json_path = os.path.join(folder_path, self._args['json_folder_name'])

        conf.log.debug("Json Path Setting Path: {}".format(json_path))
        if not os.path.isfile(json_path):
            conf.log.info("No Json File Settings Found In {}. Using Default Configuration. ".format(folder_path))
            return add_folder_altered(self._args)
        try:
            with open(json_path, 'r') as f:
                json_data = json.load(f)
        except JSONDecodeError:
            conf.log.info("Json File Settings {} Is Not In Valid JSON Format. Using Default Configuration. "
                          .format(folder_path))
            return add_folder_altered(self._args)
        try:
            a = argv.ArgvParser.config_args(argv.ArgvParser.parser.parse_args(sys.argv[1:]), json_data=json_data)
            conf.log.info("Using {} Configuration for processing {} folder. "
                          .format(json_path, folder_path))
            return add_folder_altered(a)
        except SystemExit:
            conf.log.error("Arguments json file {} contains configuration error. "
                           "Using Default Configuration".format(json_path))
            return add_folder_altered(self._args)


class GifTransform(Process):
    """
    GIF Image Processing Class
    """

    def __init__(self, input_path, phases, output_path, args=None):
        """
        ImageTransformGIF Constructor
        :param input_path: <string> gif path to process
        :param output_path: <string> image path to write the result
        :param phases: <ImageTransform[]> list of Class transformation use by the process each image
        """
        super().__init__(args=args)
        self.__phases = phases
        self.__input_path = input_path
        self.__output_path = output_path
        self.__tmp_dir = None
        self.__temp_input_paths = []
        self.__temp_output_paths = []

    def _setup(self):
        self.__tmp_dir = tempfile.mkdtemp()
        conf.log.debug("Temporay dir is {}".format(self.__tmp_dir))
        imgs = imageio.mimread(self.__input_path)
        conf.log.info("GIF have {} Frames To Process".format(len(imgs)))
        self.__temp_input_paths = [os.path.join(self.__tmp_dir, "intput_{}.png".format(i))
                                   for i in range(len(imgs))]

        self.__temp_output_paths = [os.path.join(self.__tmp_dir, "output_{}.png".format(i))
                                    for i in range(len(imgs))]

        [write_image(cv2.cvtColor(i[0], cv2.COLOR_RGB2BGR), i[1]) for i in zip(imgs, self.__temp_input_paths)]

    def _execute(self):
        """
        Execute all phases on each frames of the gif and recreate the gif
        :return: None
        """
        MultipleImageTransform(self.__temp_input_paths, self.__phases, self.__temp_output_paths, args=self._args).run()

        dir = os.path.dirname(self.__output_path)
        if dir != '':
            os.makedirs(os.path.dirname(self.__output_path), exist_ok=True)
        imageio.mimsave(self.__output_path, [imageio.imread(i) for i in self.__temp_output_paths])

        conf.log.info("{} Gif Created ".format(self.__output_path))

    def _clean(self):
        shutil.rmtree(self.__tmp_dir)
