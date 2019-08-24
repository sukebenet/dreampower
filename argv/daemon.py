import daemon
from argv.common import arg_debug, arg_help, arg_version


def init_daemon_sub_parser(subparsers):
    daemon_parser = subparsers.add_parser(
        'daemon',
        description="Running dreampower on daemon mode.",
        help="Running dreampower on daemon mode.",
        add_help=False
    )
    daemon_parser.set_defaults(func=daemon.main)

    # add daemon arguments
    arg_help(daemon_parser)
    arg_debug(daemon_parser)
    arg_version(daemon_parser)

    return daemon_parser
