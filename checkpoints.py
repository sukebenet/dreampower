"""checkpoints logic."""
import logging
import os
import shutil
import sys
import tempfile

from config import Config as Conf
from utils import setup_log, dl_file, unzip


def main(_):
    """
    Start checkpoints main logic.

    :param _: None
    :return: None
    """
    if sum([1 for x in ["cm.lib", "mm.lib", "mn.lib"] if os.path.isfile(os.path.join(Conf.args['checkpoints'], x))]):
        Conf.log.info("Checkpoints Found In {}".format(Conf.args['checkpoints']))
    else:
        Conf.log.warn("Checkpoints Not Found In {}".format(Conf.args['checkpoints']))
        Conf.log.info("You Can Download Them Using : {} checkpoints download".format(sys.argv[0]))


def download(_):
    """
    Start checkpoints download logic.

    :param _: None
    :return: None
    """
    Conf.log = setup_log(logging.DEBUG) if Conf.args['debug'] else setup_log()
    tempdir = tempfile.mkdtemp()
    cdn_url = Conf.checkpoints_cdn.format(Conf.checkpoints_version)
    temp_zip = os.path.join(tempdir, "{}.zip".format(Conf.checkpoints_version))

    try:
        Conf.log.info("Downloading {}".format(cdn_url))
        dl_file(Conf.checkpoints_cdn.format(Conf.checkpoints_version), temp_zip)
		
        if not os.path.exists(Conf.args['checkpoints']['checkpoints_path']):
            os.mkdir(Conf.args['checkpoints']['checkpoints_path'])		

        Conf.log.info("Extracting {}".format(temp_zip))
        unzip(temp_zip, Conf.args['checkpoints']['checkpoints_path'])

        Conf.log.info("Moving Checkpoints To Final Location")

        for c in ("cm.lib", "mm.lib", "mn.lib"):
            if os.path.isfile(os.path.join(Conf.args['checkpoints']['checkpoints_path'], c)):
                os.remove(os.path.join(Conf.args['checkpoints']['checkpoints_path'], c))
            shutil.move(os.path.join(Conf.args['checkpoints']['checkpoints_path'], 'checkpoints', c), Conf.args['checkpoints']['checkpoints_path'])
        shutil.rmtree(os.path.join(Conf.args['checkpoints']['checkpoints_path'], 'checkpoints'))

    except Exception as e:
        Conf.log.error(e)
        Conf.log.error("Something Gone Bad Download Downloading The Checkpoints")
        shutil.rmtree(tempdir)
        sys.exit(1)
    shutil.rmtree(tempdir)
    Conf.log.info("Checkpoints Downloaded Successfully")
