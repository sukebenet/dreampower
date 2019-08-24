from config import Config as Conf


def arg_debug(parser):
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="Enable log debug mod."
    )


def arg_help(parser):
    parser.add_argument(
        '-h',
        '--help',
        action='help',
        help='Show this help message and exit.'
    )


def arg_version(parser):
    parser.add_argument(
        "-v",
        "--version",
        action='version', version='%(prog)s {}'.format(Conf.version)
    )
