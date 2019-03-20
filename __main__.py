#!/usr/bin/env python3
# -*- coding: utf8

import argparse
import logging
from math import ceil
from glob import glob
from itertools import zip_longest
import os.path as path
from shutil import copyfile


def main():
    try:
        parser = argparse.ArgumentParser(description='Description of the program.')
        parser.add_argument('-v', '--verbose', action='count', default=0, help='verbosity level')
        parser.add_argument('-i', '--input', required=True, help='input')
        parser.add_argument('-o', '--output', default='', help='input')
        args = parser.parse_args()

        if args.verbose:
            logging.getLogger().setLevel(logging.INFO)
        if args.verbose > 1:
            logging.getLogger().setLevel(logging.DEBUG)

        input_filepath_list = list(glob(args.input))
        nb_files = len(input_filepath_list)
        logging.info('files to rename: {}.'.format(nb_files))

        middle = ceil(nb_files / 2.0)
        odd_files = input_filepath_list[0:middle]
        even_files = input_filepath_list[middle:]
        even_files.reverse()

        input_filepath_list = [f for pair in zip_longest(odd_files, even_files) for f in pair if f is not None]
        output_filepath_list = [path.join(path.dirname(f), '{num:05d}{ext}'.format(num=i, ext=path.splitext(f)[1]))
                                for i, f in enumerate(input_filepath_list)]

        for i, o in zip(input_filepath_list, output_filepath_list):
            logging.debug('rename:\n\tfrom: {i}\n\tto  : {o}'.format(i=i, o=o))
            copyfile(i, o)

    except Exception as e:
        logging.critical(e)
        if __debug__:
            raise


if __name__ == '__main__':
    main()