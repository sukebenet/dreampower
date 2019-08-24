import logging

from torch import cuda
import json as j
from config import Config as conf
from utils import setup_log


def get_info():
    return {
        "has_cuda": cuda.is_available(),
        "devices": [] if not cuda.is_available() else [cuda.get_device_name(i) for i in range(cuda.device_count())],
    }


def main(_):
    info = get_info()
    if not conf.args['json']:
        conf.log.info("Has Cuda: {}".format(info["has_cuda"]))
        for (i, device) in enumerate(info["devices"]):
            conf.log.info("GPU {}: {}".format(i, device))
    else:
        print(j.dumps(info))
