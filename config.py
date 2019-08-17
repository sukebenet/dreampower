import os


class Config:
    """
    Variables Configuration Class
    """
    # experiment specifics
    norm = "batch"  # instance normalization or batch normalization
    use_dropout = False  # use dropout for the generator
    data_type = 32  # Supported data type i.e. 8, 16, 32 bit

    # input/output sizes
    batchSize = 1  # input batch size
    input_nc = 3  # of input image channels
    output_nc = 3  # of output image channels

    # for setting inputs
    # if true, takes images in order to make batches, otherwise takes them randomly
    serial_batches = True
    nThreads = (
        0
    )  # threads for loading data. Keep this value at 0! see: https://github.com/pytorch/pytorch/issues/12831
    # Maximum number of samples allowed per dataset. If the dataset directory contains more than max_dataset_size,
    # only a subset is loaded.
    max_dataset_size = 1

    # for generator
    netG = "global"  # selects model to use for netG
    ngf = 64  # of gen filters in first conv layer
    n_downsample_global = 4  # number of downsampling layers in netG
    n_blocks_global = (
        9
    )  # number of residual blocks in the global generator network
    n_blocks_local = (
        0
    )  # number of residual blocks in the local enhancer network
    n_local_enhancers = 0  # number of local enhancers to use
    # number of epochs that we only train the outmost local enhancer
    niter_fix_global = 0

    # Phase specific options
    checkpoints_dir = ""
    dataroot = ""

    # Image requirement
    desired_size = 512

    # Argparser dict
    args = {}

    # Log
    log = None

    # Multiprocessing
    @staticmethod
    def multiprocessing():
        return Config.args['gpu_ids'] is not None and Config.args['n_cores'] > 1
