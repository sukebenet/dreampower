"""Configuration."""

def closest_number(n, m = 16) -> int:
    # Find the quotient
    q = int(n / m)

    # 1st possible closest number
    n1 = m * q

    # 2nd possible closest number
    if((n * m) > 0) :
        n2 = (m * (q + 1))
    else :
        n2 = (m * (q - 1))

    # if true, then n1 is the required closest number
    if (abs(n - n1) < abs(n - n2)) :
        return n1

    # else n2 is the required closest number
    return n2


class Config:
    """Variables Configuration Class."""

    version = "v1.2.11"
    checkpoints_version = "v0.0.1"
    checkpoints_cdn = "https://downloads.dreamnet.tech/checkpoints/{}?direct=1"

    # experiment specifics
    norm = "batch"  # instance normalization or batch normalization
    use_dropout = False  # use dropout for the generator
    data_type = 32  # Supported data type i.e. 8, 16, 32 bit

    # input/output sizes
    batch_size = 1  # input batch size
    input_nc = 3  # of input image channels
    output_nc = 3  # of output image channels

    # for setting inputs
    # if true, takes images in order to make batches, otherwise takes them randomly
    serial_batches = True
    n_threads = 0  # threads for loading data. Keep this value at 0! see: https://github.com/pytorch/pytorch/issues/12831
    # Maximum number of samples allowed per dataset. If the dataset directory contains more than max_dataset_size,
    # only a subset is loaded.
    max_dataset_size = 1

    # for generator
    net_g = "global"  # selects model to use for net_g
    ngf = 64  # of gen filters in first conv layer
    n_downsample_global = 4  # number of downsampling layers in net_g
    n_blocks_global = (
        9
    )  # number of residual blocks in the global generator network
    n_blocks_local = (
        0
    )  # number of residual blocks in the local enhancer network
    n_local_enhancers = 0  # number of local enhancers to use
    # number of epochs that we only train the outmost local enhancer
    niter_fix_global = 0

    # Image requirement
    desired_size = 512
    desired_shape = desired_size, desired_size, 3

    # Argparser dict
    args = {}

    # Log
    log = None

    # Multiprocessing
    @staticmethod
    def multiprocessing():
        """
        Return multiprocessing status.

        :return: <boolean> True is multiprocessing can be use
        """
        return Config.cores() > 1

    @staticmethod
    def cuda_multiprocessing():
        """
        Return multiprocessing status.

        :return: <boolean> True is multiprocessing can be use
        """
        return Config.args['gpu_ids'] is None and Config.cores() > 1

    @staticmethod
    def set_image_size(size):
      Config.desired_size = closest_number(size)
      Config.desired_shape = (Config.desired_size, Config.desired_size, 3)
      Config.log.info("Desired Image Size: {}".format(Config.desired_size))

    @staticmethod
    def cores():
      cores = 1

      if Config.args['n_cores'] and Config.args['n_cores'] > 0:
        cores = Config.args['n_cores']

      return cores
