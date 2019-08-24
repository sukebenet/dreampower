import os
import sys
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from config import Config as conf
from transform.gan.mask import CorrectToMask, MaskrefToMaskdet, MaskfinToNude
from transform.opencv.correct import DressToCorrect
from transform.opencv.mask import MaskToMaskref, MaskdetToMaskfin


class Watcher:
    def __init__(self, watching_dir, out_dir):
        self.__observer = Observer()
        self.__watching_dir = watching_dir
        self.__out_dir = out_dir

        if not os.path.isdir(self.__watching_dir):
            conf.log.error("{} Watching Dir Doesn't Exit.".format(self.__watching_dir))
            sys.exit(0)

        if not os.path.isdir(self.__out_dir):
            conf.log.error("{} Output Dir Doesn't Exit.".format(self.__watching_dir))
            sys.exit(0)

    def run(self):
        event_handler = Handler(self.__out_dir)
        self.__observer.schedule(event_handler, self.__watching_dir, recursive=True)
        self.__observer.start()
        try:
            while True:
                time.sleep(5)
        except KeyboardInterrupt:
            self.__observer.stop()
        except Exception as e:
            self.__observer.stop()
            conf.log.error(e)
            conf.log.error("An Unhandled Error Occurred.")
            sys.exit(1)
        self.__observer.join()


class Handler(FileSystemEventHandler):
    def __init__(self, out_dir):
        self.__out_dir = out_dir
        self.__phases = [
            DressToCorrect, CorrectToMask, MaskToMaskref, MaskrefToMaskdet, MaskdetToMaskfin, MaskfinToNude
        ]

    def on_created(self, event):
        if event.is_directory:
            conf.log.debug("Received directory created event {}.".format(event.src_path))
            # TODO Implements this


def main():
    Watcher("test_dir", "out_dir").run()

