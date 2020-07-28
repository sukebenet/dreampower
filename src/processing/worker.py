""" Wokers definition """
# TODO Implement this with a queue and mutliprocessingt
import threading

from config import Config as Conf
from transform.gan.mask import CorrectToMask, MaskrefToMaskdet, MaskfinToNude
from transform.opencv.correct import DressToCorrect, ColorTransfer
from transform.opencv.mask import MaskToMaskref, MaskdetToMaskfin
from transform.opencv.resize import ImageToResized, ImageToCrop, ImageToOverlay, ImageToResizedCrop, ImageToRescale, ImageToNearest, ImageCompress

workers = {
    "gan": {
        CorrectToMask: [],
        MaskrefToMaskdet: [],
        MaskfinToNude: [],
        "sem": threading.Semaphore(1)
    },
    "opencv": {
        DressToCorrect: [],
        MaskToMaskref: [],
        ImageToResized: [],
        ImageToCrop: [],
        ImageToOverlay: [],
        ImageToResizedCrop: [],
        ImageToRescale: [],
        ImageToNearest: [],
        ImageCompress: [],
        ColorTransfer: [],
        MaskdetToMaskfin: [],
        "sem": threading.Semaphore(Conf.cores())
    }
}
select_sem = threading.Semaphore(1)


def run_worker(klass, image_step, config=None):
    r = None
    for k in ("gan", "opencv"):
        if workers.get(k).get(klass) is not None:
            #Conf.log.debug("wk {}".format(workers.get(k).get(klass)))

            workers.get(k).get("sem").acquire()

            select_sem.acquire()
            if len(workers.get(k).get(klass)) == 0:
                w = klass()
            else:
                w = workers.get(k).get(klass).pop(0)
            select_sem.release()

            r = w.run(*[image_step[i] for i in w.input_index], config=config)

            select_sem.acquire()
            workers.get(k).get(klass).append(w)
            select_sem.release()

            workers.get(k).get("sem").release()
    return r
