import logging
import os
import shutil
import sys
import tempfile

from config import Config as conf
from utils import setup_log, dl_file, unzip


def main(_):
    if sum([1 for x in ["cm.lib", "mm.lib", "mn.lib"] if os.path.isfile(os.path.join(conf.args['checkpoints'], x))]):
        conf.log.info("Checkpoints Found In {}".format(conf.args['checkpoints']))
    else:
        conf.log.warn("Checkpoints Not Found In {}".format(conf.args['checkpoints']))
        conf.log.info("You Can Download Them Using : {} checkpoints download".format(sys.argv[0]))


def download(_):
    conf.log = setup_log(logging.DEBUG) if conf.args['debug'] else setup_log()
    tempdir = tempfile.mkdtemp()
    cdn_url = conf.checkpoints_cdn.format(conf.checkpoints_version)
    temp_zip = os.path.join(tempdir, "{}.zip".format(conf.checkpoints_version))

    try:
        conf.log.info("Downloading {}".format(cdn_url))
        dl_file(conf.checkpoints_cdn.format(conf.checkpoints_version), temp_zip)

        conf.log.info("Extracting {}".format(temp_zip))
        unzip(temp_zip, conf.args['checkpoints'])

        conf.log.info("Moving Checkpoints To Final Location")

        for c in ("cm.lib", "mm.lib", "mn.lib"):
            if os.path.isfile(os.path.join(conf.args['checkpoints'], c)):
                os.remove(os.path.join(conf.args['checkpoints'], c))
            shutil.move(os.path.join(conf.args['checkpoints'], 'checkpoints', c), conf.args['checkpoints'])
        shutil.rmtree(os.path.join(conf.args['checkpoints'], 'checkpoints'))

    except Exception as e:
        conf.log.error(e)
        conf.log.error("Something Gone Bad Download Downloading The Checkpoints")
        shutil.rmtree(tempdir)
        sys.exit(1)
    shutil.rmtree(tempdir)
    conf.log.info("Checkpoints Downloaded Successfully")