#!/usr/bin/env python3
# -*- coding: utf8

import argparse
import os.path as path
import logging, sys
import tkinter as tk
from core import rectoverso
from DebrotherMainWindow import DebrotherMainWindow

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))


def rectoverso_main():
    try:
        cli_parser = argparse.ArgumentParser(
            description='debɹother re-order and rename files (images) from brother scanner.')
        cli_parser.add_argument('-v', '--verbose', action='count', default=0,
                                help='verbosity level')
        cli_parser.add_argument('-i', '--input',
                                help='input')
        cli_parser.add_argument('-o', '--output',
                                help='output directory [same as input]')
        cli_parser.add_argument('-c', '--config', default='debrother.ini',
                                help='path to config file[debrother.ini]')
        cli_parser.add_argument('--pattern',
                                help='output file name syntax.')
        cli_parser.add_argument('-q', '--quiet', action='store_true',
                                help='no gui')
        cli_parser.add_argument('--debug', action='store_true', default=False,
                                help='debug mode on')
        args = cli_parser.parse_args()

        if args.verbose:
            logger.setLevel(logging.INFO)
        if args.verbose > 1:
            logger.setLevel(logging.DEBUG)

        args.config = path.abspath(args.config)
        logger.info(
            'config:\n' + '\n'.join(f'\t--{k:10} {v}' for k, v in args.__dict__.items())
        )

        if args.quiet:
            rectoverso(args.input, args.output, args.pattern)
        else:
            logger.debug('init GUI')
            root = tk.Tk()
            my_gui = DebrotherMainWindow(root, **vars(args))
            root.mainloop()
            logger.debug('exiting')

    except Exception as e:
        logger.critical(e)
        if args.debug:
            raise


if __name__ == '__main__':
    rectoverso_main()
