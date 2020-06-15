"""Folder Image Transform Processing."""
import copy
import json
import os
import pathlib
import sys
from json import JSONDecodeError

from config import Config as Conf
from processing.multiple import MultipleImageProcessing
from processing.utils import select_phases, is_file
from utils import is_a_supported_image_file_extension


class FolderImageProcessing(MultipleImageProcessing):
    """Folder Image Processing Class."""
    def _setup(self, *args):
        self._input_folder_path = self._args['input']
        self._output_folder_path = self._args['output']
        self._multiprocessing = Conf.multiprocessing()
        self._process_list = []
        Conf.log.debug([(r, d, f) for r, d, f in os.walk(self._input_folder_path)])

        for r, _, _ in os.walk(self._input_folder_path):
            args = copy.deepcopy(self._args)
            args['input'] = [
                x.path for x in os.scandir(r) if is_file(args, x.path) and is_a_supported_image_file_extension(x.path)
            ]
            args['phases'] = select_phases(self._args)
            args['output'] = [
                "{}{}{}".format(
                    os.path.splitext(x)[0],
                    '_out',
                    os.path.splitext(x)[1]
                )
                if not Conf.args['output'] else
                os.path.join(
                    Conf.args['output'],
                    pathlib.Path(*pathlib.Path(r).parts[1:]),
                    os.path.basename(x)
                )
                for x in args['input']
            ]

            self._process_list.append(
                (MultipleImageProcessing(), self.__get_folder_args(args, r))
            )

    @staticmethod
    def __get_folder_args(args, folder_path):
        def add_folder_altered(args):
            if args.get('altered'):
                args['folder_altered'] = os.path.join(args['altered'],
                                                      pathlib.Path(*pathlib.Path(folder_path).parts[1:]))
            return args

        json_path = os.path.join(folder_path, args['json_folder_name'])

        Conf.log.debug("Json Path Setting Path: {}".format(json_path))
        if not os.path.isfile(json_path):
            Conf.log.info("No Json File Settings Found In {}. Using Default Configuration. ".format(folder_path))
            return add_folder_altered(args)
        try:
            with open(json_path, 'r') as f:
                json_data = json.load(f)
        except JSONDecodeError:
            Conf.log.info("Json File Settings {} Is Not In Valid JSON Format. Using Default Configuration. "
                          .format(folder_path))
            return add_folder_altered(args)
        try:
            from argv import Parser, config_args
            a = config_args(Parser.parser, Parser.parser.parse_args(sys.argv[1:]), json_data=json_data)
            Conf.log.info("Using {} Configuration for processing {} folder. "
                          .format(json_path, folder_path))
            return add_folder_altered(a)
        except SystemExit:
            Conf.log.error("Arguments json file {} contains configuration error. "
                           "Using Default Configuration".format(json_path))
            return add_folder_altered(args)
