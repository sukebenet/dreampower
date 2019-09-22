import main
from argv.checkpoints import arg_checkpoints
from argv.common import arg_debug, arg_help, arg_version
from argv.run.argument import arg_altered, arg_auto_rescale, arg_auto_resize, arg_auto_resize_crop, arg_color_transfer,\
    arg_cpu, arg_gpu, arg_ignore_size, arg_input, arg_json_args, arg_json_folder_name, arg_n_run, \
    arg_output, arg_overlay, arg_preferences, arg_step, arg_gan_persistent


def init_run_parser(subparsers):
    run_parser = subparsers.add_parser(
        'run',
        description="Process image(s) with dreampower.",
        help="Process image(s) with dreampower.",
        add_help=False
    )
    run_parser.set_defaults(func=main.main)

    # conflicts handler
    processing_mod = run_parser.add_mutually_exclusive_group()
    scale_mod = run_parser.add_mutually_exclusive_group()

    # add run arguments
    arg_input(run_parser)
    arg_output(run_parser)

    arg_auto_rescale(scale_mod)
    arg_auto_resize(scale_mod)
    arg_auto_resize_crop(scale_mod)
    arg_overlay(scale_mod)
    arg_ignore_size(scale_mod)

    arg_color_transfer(run_parser)

    arg_preferences(run_parser)
    arg_n_run(run_parser)
    arg_step(run_parser)
    arg_altered(run_parser)

    arg_cpu(processing_mod)
    arg_gpu(processing_mod)
    arg_checkpoints(run_parser)
    # arg_n_core(run_parser) TODO Broken Fix this
    arg_gan_persistent(run_parser)

    arg_json_args(run_parser)
    arg_json_folder_name(run_parser)

    arg_help(run_parser)
    arg_debug(run_parser)
    arg_version(run_parser)
