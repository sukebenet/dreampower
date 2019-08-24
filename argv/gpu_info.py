import gpu_info
from argv.common import arg_debug, arg_help, arg_version


def init_gpu_info_sub_parser(subparsers):
    gpu_info_parser = subparsers.add_parser(
        'gpu-info',
        description="Getting GPU capabilities information for processing with dreampower",
        help="Getting GPU capabilities information for processing with dreampower",
        add_help=False
    )
    gpu_info_parser.set_defaults(func=gpu_info.main)

    # add gpu-info arguments
    arg_json(gpu_info_parser)

    arg_help(gpu_info_parser)
    arg_debug(gpu_info_parser)
    arg_version(gpu_info_parser)

    return gpu_info_parser


def arg_json(parser):
    parser.add_argument(
        "-j",
        "--json",
        action='store_true',
        help=""
    )
