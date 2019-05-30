#!/usr/bin/env python3
# -*- coding: utf8

import argparse
import logging
from glob import glob
import re
import os
import os.path as path
from shutil import copyfile

from tkinter import filedialog
import tkinter as tk
from tkinter import ttk

windows_scan_naming_convention = re.compile(r'(?P<base>.+_(\d){8})(_(?P<page>\d+))?(\s\((?P<batch>\d+)\))?\.\w+$')


def populate_pages(input_dirpath):
    """
    input_dirpath:
        Numérisation_20190412 (2).jpg
        Numérisation_20190412.jpg
        Numérisation_20190412_10 (2).jpg
        Numérisation_20190412_10.jpg
        Numérisation_20190412_11 (2).jpg
        Numérisation_20190412_11.jpg
        ...
        Numérisation_20190412_1 (2).jpg
        Numérisation_20190412_1.jpg
    """
    file_list = [path.join(p, filename)
                 for p, sd, fs in os.walk(input_dirpath)
                 for filename in fs
                 if windows_scan_naming_convention.match(filename)]

    return sorted(file_list)


def sort_brother_pages(file_list):
    """
    :param file_list:
    :return:
    """
    brother_numbering_template = re.compile(r'_(?P<date>\d{8})(_(?P<num>\d+))?')

    def get_brother_number(filepath):
        return int(brother_numbering_template.search(filepath).groupdict()['num'] or '1')

    return sorted(file_list, key=get_brother_number)


def sort_widnows_files(file_list):
    """
    returns files order per pages and then batch :
        ['xxx.jpg', 'xxx (2).jpg', 'yyy.jpg', 'yyy (2).jpg']
        -->
        ['xxx.jpg', 'yyy.jpg', 'xxx (2).jpg', 'yyy (2).jpg']
    """
    windows_batch_template = re.compile(r'(\s\((?P<batch>\d+)\))?\.\w+$')

    def get_windows_batch_number(filepath):
        return int(windows_batch_template.search(filepath).groupdict()['batch'] or '1')

    return sorted(file_list, key=get_windows_batch_number)


def sort_reversed_verso(file_list):
    """
    [1,3,5,6,4,2] -> [1,2,3,4,5,6]
    """
    nb_pages = len(file_list)
    result = [None] * nb_pages
    result[0::2] = file_list[0:nb_pages//2]
    result[1::2] = reversed(file_list[nb_pages//2:])
    return result


def get_output_filepaths(input_filepath_list, output_dirpath):
    input_infos_list = [{
        'original': filepath,
        'page': page,
        'filename': path.basename(filepath),
        'basename': path.splitext(path.basename(filepath))[0],
        'ext': path.splitext(path.basename(filepath))[1][1:],
    } for page, filepath in enumerate(input_filepath_list)]

    return [output_dirpath.format(**infos) for infos in input_infos_list]


def rectoverso(input_dirpath, output_dirpath):
    input_filepath_list = populate_pages(input_dirpath)
    nb_files = len(input_filepath_list)
    logging.info('files to rename: {}.'.format(nb_files))

    input_filepath_list = sort_widnows_files(input_filepath_list)
    input_filepath_list = sort_reversed_verso(input_filepath_list)
    output_filepath_list = get_output_filepaths(input_filepath_list, output_dirpath)

    for i, o in zip(input_filepath_list, output_filepath_list):
        logging.debug('rename:\n\tfrom: {i}\n\tto  : {o}'.format(i=i, o=o))
        copyfile(i, o)


class RectoVersoMainWindow(tk.Frame):
    def __init__(self, master, **options):
        PAD = 10
        self.master = master
        super().__init__(self.master, padx=PAD, pady=PAD)
        self.master.title("RE order")
        self.pack(fill=tk.BOTH, expand=tk.TRUE)

        master.geometry("800x800")
        # VARs
        self.input_dirpath = tk.StringVar()
        self.output_dirpath = tk.StringVar()
        self.filename_pattern = tk.StringVar()
        self.input_file_list = {}
        self.is_brother_checked = tk.IntVar()
        self.is_windows_checked = tk.IntVar()
        self.is_reversed_checked = tk.IntVar()

        if 'input' in options:
            self.input_dirpath.set(options['input'])
        if 'output' in options:
            self.output_dirpath.set(options['output'])

        # GUIS
        settings_frame = tk.LabelFrame(self, text='settings', padx=PAD//2, pady=PAD//2)
        settings_frame.pack(fill=tk.BOTH, expand=tk.FALSE, side=tk.TOP, padx=PAD//2, pady=PAD//2)
        # input
        input_frame = tk.Frame(settings_frame)
        input_frame.pack(fill=tk.BOTH, expand=tk.TRUE, side=tk.TOP)
        input_dir_selector = tk.Frame(input_frame, padx=PAD//2, pady=PAD//2)
        input_dir_selector.pack(fill=tk.X, expand=tk.FALSE, side=tk.TOP)
        input_dir_label = tk.Label(input_dir_selector, text='input:')
        input_dir_label.pack(fill=tk.X, expand=tk.FALSE, side=tk.LEFT)
        input_dir_path = tk.Entry(input_dir_selector, textvariable=self.input_dirpath)
        input_dir_path.pack(fill=tk.X, expand=tk.TRUE, side=tk.LEFT)
        input_dir_button = tk.Button(input_dir_selector, text="...", command=self.on_browse_input)
        input_dir_button.pack(side=tk.LEFT, padx=PAD//2)
        # output
        output_frame = tk.Frame(settings_frame)
        output_frame.pack(fill=tk.BOTH, expand=tk.TRUE, side=tk.TOP)
        output_dir_selector = tk.Frame(output_frame, padx=PAD//2, pady=PAD//2)
        output_dir_selector.pack(fill=tk.X, expand=tk.FALSE, side=tk.TOP)
        output_dir_label = tk.Label(output_dir_selector, text='ouput:')
        output_dir_label.pack(fill=tk.X, expand=tk.FALSE, side=tk.LEFT)
        output_dir_path = tk.Entry(output_dir_selector, textvariable=self.output_dirpath)
        output_dir_path.pack(fill=tk.X, expand=tk.TRUE, side=tk.LEFT)
        output_dir_button = tk.Button(output_dir_selector, text="...", command=self.on_browse_output)
        output_dir_button.pack(side=tk.LEFT, padx=PAD//2)

        self.input_file_cols = ['name', 'sheet', 'side']
        self.input_file_view = ttk.Treeview(self, columns=self.input_file_cols, show=['headings'])
        self.input_file_view.pack(fill=tk.BOTH, expand=tk.TRUE, side=tk.TOP, padx=PAD//2, pady=PAD//2)
        self.input_file_view.heading("#0", text="#", anchor=tk.W)
        self.input_file_view.column("#0", width=10)
        for col_name in self.input_file_cols:
            # self.input_file_view.column(col_name, width=50)
            self.input_file_view.heading(col_name, text=col_name)

        # options
        options_frame = tk.LabelFrame(self, text='options', padx=PAD//2, pady=PAD//2)
        options_frame.pack(padx=PAD//2, pady=PAD//2, fill=tk.X, expand=tk.FALSE, side=tk.TOP)
        button = tk.Checkbutton(options_frame, text="brother", command=self.on_option, variable=self.is_brother_checked)
        button.pack(side=tk.LEFT)
        button = tk.Checkbutton(options_frame, text="windows", command=self.on_option, variable=self.is_windows_checked)
        button.pack(side=tk.LEFT)
        button = tk.Checkbutton(options_frame, text="reversed", command=self.on_option, variable=self.is_reversed_checked)
        button.pack(side=tk.LEFT)

        button = tk.Button(options_frame, text="proceed", command=self.on_proceed)
        button.pack(side=tk.RIGHT)

        self.is_brother_checked.set(1)
        self.is_windows_checked.set(1)
        self.is_reversed_checked.set(1)

        self.populate()

    def on_browse_input(self):
        browse_dirpath = tk.filedialog.askdirectory(title="Select scanned directory",
                                                  initialdir=self.input_dirpath.get(),)
        if browse_dirpath:
            self.input_dirpath.set(browse_dirpath)
            self.populate()

    def on_populate(self):
        self.populate()

    def on_browse_output(self):
        browse_dirpath = tk.filedialog.askdirectory(title="Select output directory",
                                                  initialdir=self.output_dirpath.get(),)
        if browse_dirpath:
            self.output_dirpath.set(browse_dirpath)

    def on_option(self):
        self.populate()

    def on_proceed(self):
        rectoverso(self.input_dirpath.get(), self.output_dirpath.get())

    def populate(self):
        filepaths = populate_pages(self.input_dirpath.get())
        filepaths = (path.relpath(f, self.input_dirpath.get()) for f in filepaths)

        if self.is_brother_checked.get():
            filepaths = sort_brother_pages(filepaths)

        if self.is_windows_checked.get():
            filepaths = sort_widnows_files(filepaths)

        if self.is_reversed_checked.get():
            filepaths = sort_reversed_verso(filepaths)

        self.input_file_list = {}

        self.input_file_view.delete(*self.input_file_view.get_children())
        for i, f in enumerate(filepaths):
            self.input_file_view.insert('', 'end', text=i, values=(f, 'a', "1b"))


def rectoverso_main():
    try:
        parser = argparse.ArgumentParser(description='rectoverso re-order and rename files (images) from scan.')
        parser.add_argument('-v', '--verbose', action='count', default=0, help='verbosity level')
        parser.add_argument('-i', '--input', required=False, help='input')
        parser.add_argument('-o', '--output', default='', help='input')
        parser.add_argument('-q', '--quiet', action='store_true', help='no gui')
        parser.add_argument('--debug', action='store_true', default=False, help='debug mode on')
        args = parser.parse_args()

        if args.verbose:
            logging.getLogger().setLevel(logging.INFO)
        if args.verbose > 1:
            logging.getLogger().setLevel(logging.DEBUG)

        if args.quiet:
            rectoverso(args.input, args.output, **vars(args))
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