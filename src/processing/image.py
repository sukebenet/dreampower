"""Image Transform Processing."""
import os
import sys
import hashlib
import time
import torch

from config import Config as Conf
from processing import Processing
from processing.utils import select_phases
from processing.worker import run_worker
from multiprocessing.pool import ThreadPool
from utils import camel_case_to_str, write_image
from loader import Loader
from transform.gan.model import DeepModel


class ImageProcessing(Processing):
    """Image Processing Class."""
    def _setup(self, *args):
        """
        Process Image Constructor.

        :param args: <dict> args parameter to run the image transformation (default use Conf.args)
        """
        self.__phases = select_phases(self._args)
        self.__input_path = self._args['input']
        self.__output_path = self._args['output']
        self.__altered_path = self._args.get('altered')
        self.__masks_path = self._args.get('masks_path')
        self.__starting_step = self._args['steps'][0] if self._args.get('steps') else 0
        self.__ending_step = self._args['steps'][1] if self._args.get('steps') else None

        Conf.log.debug("")
        Conf.log.spam("All Phases : {}".format(self.__phases))
        if self.__ending_step != None and self.__ending_step > 0:
          Conf.log.spam("Steps: {}:{} ({}:{})".format(self.__starting_step, self.__ending_step - 1, self.__starting_step, self.__ending_step))
        else:
          Conf.log.spam("Steps: {}:{}".format(self.__starting_step, self.__ending_step))
        Conf.log.debug("To Be Executed Phases : {}".format(self.__phases[self.__starting_step:self.__ending_step]))

        imagename_no_ext = os.path.splitext(os.path.basename(self.__input_path))[0]

        if (self._args.get('folder_altered')):
            folder_name = imagename_no_ext + '_' + str(hashlib.md5(open(self.__input_path, 'rb').read()).hexdigest())
            folder_path = os.path.join(self._args['folder_altered'], folder_name)

            if (not os.path.isdir(folder_path)):
               os.makedirs(folder_path, exist_ok=True)

            self._args['folder_altered'] = folder_path
            path = self._args['folder_altered']

            self.__image_steps = [self.__input_path] + [
                os.path.join(path, "{}.png".format(p().__class__.__name__))
                for p in self.__phases[:self.__starting_step]
            ]
        elif (self.__altered_path):
            folder_name = imagename_no_ext + '_' + str(hashlib.md5(open(self.__input_path, 'rb').read()).hexdigest())
            folder_path = os.path.join(self.__altered_path, folder_name)

            if (not os.path.isdir(folder_path)):
               os.makedirs(folder_path, exist_ok=True)

            self.__altered_path = folder_path
            path = self.__altered_path

            self.__image_steps = [self.__input_path] + [
                os.path.join(path, "{}.png".format(p().__class__.__name__))
                for p in self.__phases[:self.__starting_step]
            ]
        elif (self.__masks_path):
          folder_path = self.__masks_path

          self.__image_steps = [self.__input_path] + [
              os.path.join(folder_path, "{}.png".format(p().__class__.__name__))
              for p in self.__phases[:self.__starting_step]
          ]
        else:
            # TODO: refactor me, please!
            self.__image_steps = [self.__input_path] + [
                self.__input_path
                for p in self.__phases[:self.__starting_step]
            ]

        Conf.log.info("Processing on {}".format(str(self.__image_steps)))

        #self.__image_steps = [
            #    (Loader.get_loader(x)).load(x) if isinstance(x, str) else x for x in self.__image_steps
            #]

        for it,x in enumerate(self.__image_steps):
          try:
            value = (Loader.get_loader(x)).load(x) if isinstance(x, str) else x
            self.__image_steps[it] = value
          except (FileNotFoundError, AttributeError) as e:
              if (self.__altered_path):
                  Conf.log.error(e)
                  Conf.log.error("{} is not able to resume because it not able to load required images. "
                              .format(camel_case_to_str(self.__class__.__name__)))
                  Conf.log.error("Possible source of this error is that --altered argument is not a correct "
                              "directory path that contains valid images.")
                  sys.exit(1)
              else:
                  Conf.log.warning(e)

    def _execute(self, *args):
        """
        Execute all phases on the image.

        :return: None
        """
        for step,p in enumerate(x for x in self.__phases[self.__starting_step:self.__ending_step]):
            r = run_worker(p, self.__image_steps, config=self._args)
            self.__image_steps.append(r)

            if self.__altered_path:
                if (self._args.get('folder_altered')):
                    path = self._args['folder_altered']
                else:
                    path = self.__altered_path

                write_image(r, os.path.join(path, "{}.png".format(p.__name__)))

                Conf.log.spam("{} Step Image Of {} Execution".format(
                    os.path.join(path, "{}.png".format(p.__name__)),
                    camel_case_to_str(p.__name__),
                ))
            elif self.__masks_path:
                path = self.__masks_path

                write_image(r, os.path.join(path, "{}.png".format(p.__name__)))

                Conf.log.spam("{} Step Image Of {} Execution".format(
                    os.path.join(path, "{}.png".format(p.__name__)),
                    camel_case_to_str(p.__name__),
                ))

        write_image(self.__image_steps[-1], self.__output_path)
        Conf.log.info("{} Created".format(self.__output_path))
        Conf.log.debug("{} Result Image Of {} Execution"
                       .format(self.__output_path, camel_case_to_str(self.__class__.__name__)))

        return self.__image_steps[-1]
