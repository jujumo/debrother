#!/usr/bin/env python3
# -*- coding: utf8

import argparse
import os.path as path
import logging, sys
import tkinter as tk
from core import rectoverso
from DebrotherMainWindow import DebrotherMainWindow

logger = logging.getLogger('deborther')
logger.addHandler(logging.StreamHandler(sys.stdout))


class VerbosityParsor(argparse.Action):
    """ accept debug, info, ... or theirs corresponding integer value formatted as string."""
    def __call__(self, parser, namespace, values, option_string=None):
        try:  # in case it represent an int, directly get it
            values = int(values)
        except ValueError:  # else ask logging to sort it out
            assert isinstance(values, str)
            values = logging.getLevelName(values.upper())
        setattr(namespace, self.dest, values)


def rectoverso_main():
    try:
        cli_parser = argparse.ArgumentParser(
            description='debɹother re-order and rename files (images) from brother scanner.')
        parser_verbosity = cli_parser.add_mutually_exclusive_group()
        parser_verbosity.add_argument(
            '-v', '--verbose', nargs='?', default=logging.WARNING, const=logging.INFO, action=VerbosityParsor,
            help='verbosity level (debug, info, warning, critical, ... or int value) [warning]')
        parser_verbosity.add_argument(
            '-q', '--silent', '--quiet', action='store_const', dest='verbose', const=logging.CRITICAL)
        cli_parser.add_argument('-i', '--input',
                                help='input')
        cli_parser.add_argument('-o', '--output',
                                help='output directory [same as input]')
        cli_parser.add_argument('-c', '--config', default='debrother.ini',
                                help='path to config file[debrother.ini]')
        cli_parser.add_argument('--pattern',
                                help='output file name syntax.')
        cli_parser.add_argument('--nogui', action='store_true',
                                help='no gui')
        cli_parser.add_argument('--debug', action='store_true', default=False,
                                help='debug mode on')
        args = cli_parser.parse_args()


        logger.setLevel(args.verbose)

        args.config = path.abspath(args.config)
        logger.info(
            'config:\n' + '\n'.join(f'\t--{k:10} {v}' for k, v in args.__dict__.items())
        )

        if args.nogui:
            rectoverso(args.input, args.output, args.pattern)
        else:
            logger.debug('init GUI')
            root = tk.Tk()
            my_gui = DebrotherMainWindow(root, **vars(args))
            root.mainloop()
            logger.debug('exiting')

    except Exception as e:
        logger.critical(e)
        if args.verbose <= logging.DEBUG:
            raise


if __name__ == '__main__':
    rectoverso_main()
