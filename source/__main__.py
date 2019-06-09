#!/usr/bin/env python3
# -*- coding: utf8

import argparse
import logging
import tkinter as tk
from core import rectoverso
from main_gui import RectoVersoMainWindow


def rectoverso_main():
    try:
        parser = argparse.ArgumentParser(description='rectoverso re-order and rename files (images) from scan.')
        parser.add_argument('-v', '--verbose', action='count', default=0, help='verbosity level')
        parser.add_argument('-i', '--input', required=False, help='input')
        parser.add_argument('-o', '--output', default=None, help='output directory [same as input]')
        parser.add_argument('--pattern', default='{page:03d}.{ext}', help='output file name syntax.')
        parser.add_argument('-q', '--quiet', action='store_true', help='no gui')
        parser.add_argument('--debug', action='store_true', default=False, help='debug mode on')
        args = parser.parse_args()

        if args.verbose:
            logging.getLogger().setLevel(logging.INFO)
        if args.verbose > 1:
            logging.getLogger().setLevel(logging.DEBUG)

        if args.quiet:
            rectoverso(args.input, args.output, args.pattern)
        else:
            root = tk.Tk()
            my_gui = RectoVersoMainWindow(root, **vars(args))
            root.mainloop()

    except Exception as e:
        logging.critical(e)
        if args.debug:
            raise


if __name__ == '__main__':
    rectoverso_main()
