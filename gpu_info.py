"""gpu-info logic."""
import json as j

from torch import cuda

from config import Config as Conf


def get_info():
    """
    Get gpu info.

    :return: <dict> gpu info
    """
    return {
        "has_cuda": cuda.is_available(),
        "devices": [] if not cuda.is_available() else [cuda.get_device_name(i) for i in range(cuda.device_count())],
    }


def main(_):
    """
    Start gpu info main logic.

    :param _: None
    :return: None
    """
    info = get_info()
    if not Conf.args['json']:
        Conf.log.info("Has Cuda: {}".format(info["has_cuda"]))
        for (i, device) in enumerate(info["devices"]):
            Conf.log.info("GPU {}: {}".format(i, device))
    else:
        print(j.dumps(info))
