import os
import sys

import checkpoints
from config import Config as Conf
from argv.common import arg_help, arg_debug


def init_checkpoints_sub_parser(subparsers):
    checkpoints_parser = subparsers.add_parser(
        'checkpoints',
        description="Handle checkpoints for dreampower.",
        help="Handle checkpoints for dreampower.",
        add_help=False
    )

    # add checkpoints arguments
    arg_checkpoints(checkpoints_parser)

    arg_help(checkpoints_parser)
    arg_debug(checkpoints_parser)
    arg_version(checkpoints_parser)

    # add download subparser
    checkpoints_parser_subparser = checkpoints_parser.add_subparsers()
    checkpoints_parser_info_parser = checkpoints_parser_subparser.add_parser(
        'download',
        description="Download checkpoints for dreampower.",
        help="Download checkpoints for dreampower."
    )

    checkpoints_parser.set_defaults(func=checkpoints.main)
    checkpoints_parser_info_parser.set_defaults(func=checkpoints.download)

    return checkpoints_parser


def set_args_checkpoints_parser(args):
    set_arg_checkpoints(args)


def check_args_checkpoints_parser(parser, args):
    check_arg_checkpoints(parser, args)


def check_arg_checkpoints(parser, args):
    #Conf.log.debug(args.checkpoints)
    if not ('download' in str(args.func)):
        for _, v in args.checkpoints.items():
            if (_ != 'checkpoints_path' and not os.path.isfile(v)):
                parser.error(
                    "Checkpoints file not found! "
                    "You can download them using : {} checkpoints download".format(sys.argv[0])
                )


def set_arg_checkpoints(args):
    #Conf.log.debug(args.checkpoints)
    args.checkpoints = {
        'correct_to_mask': os.path.join(str(args.checkpoints), "cm.lib"),
        'maskref_to_maskdet': os.path.join(str(args.checkpoints), "mm.lib"),
        'maskfin_to_nude': os.path.join(str(args.checkpoints), "mn.lib"),
        'checkpoints_path': str(args.checkpoints),
    }


def arg_checkpoints(parser):
    parser.add_argument(
        "-c",
        "--checkpoints",
        default=os.path.join(os.getcwd(), "checkpoints"),
        help="Path of the directory containing the checkpoints. Default : ./checkpoints"
    )


def arg_version(parser):
    parser.add_argument(
        "-v",
        "--version",
        action='version', version='checkpoints {}'.format(Conf.checkpoints_version)
    )
