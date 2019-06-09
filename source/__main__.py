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

from core import populate_pages, sort_policy, get_output_filepaths, rectoverso


class RectoVersoMainWindow(tk.Frame):
    def __init__(self, master, **options):
        self.master = master
        super().__init__(self.master, padx=10, pady=10)
        self.master.title("RE order")
        self.pack(fill=tk.BOTH, expand=tk.TRUE)

        master.geometry("800x800")
        # VARs
        self.input_dirpath = tk.StringVar()
        self.output_dirpath = tk.StringVar()
        self.output_pattern = tk.StringVar()
        self.output_pattern.trace("w", lambda a,b,c : self.on_option())
        self.is_numbering_checked = tk.IntVar()
        self.is_numbering_checked.trace("w", lambda a, b, c : self.on_option())
        self.is_flip_checked = tk.IntVar()
        self.is_flip_checked.trace("w", lambda a, b, c : self.on_option())
        self.is_reversed_checked = tk.IntVar()
        self.is_reversed_checked.trace("w", lambda a,b,c : self.on_option())
        self.column_sort = tk.IntVar()
        self.column_sort.trace("w", lambda a,b,c : self.on_option())

        if 'input' in options:
            self.input_dirpath.set(options['input'])
        if 'output' in options:
            self.output_dirpath.set(options['output'])

        # GUIS
        PAD = 10
        LABEL_OPT = {'width': 10, 'anchor': tk.W}
        settings_frame = tk.LabelFrame(self, text='settings', padx=PAD//2, pady=PAD//2)
        settings_frame.pack(fill=tk.BOTH, expand=tk.FALSE, side=tk.TOP, padx=PAD//2, pady=PAD//2)
        # input
        input_frame = tk.Frame(settings_frame)
        input_frame.pack(fill=tk.BOTH, expand=tk.TRUE, side=tk.TOP)
        # input dir
        current_frame = tk.Frame(input_frame, padx=PAD//2, pady=PAD//2)
        current_frame.pack(fill=tk.X, expand=tk.FALSE, side=tk.TOP)
        label = tk.Label(current_frame, text='input:', **LABEL_OPT)
        label.pack(fill=tk.X, expand=tk.FALSE, side=tk.LEFT)
        input_dir_path = tk.Entry(current_frame, textvariable=self.input_dirpath)
        input_dir_path.pack(fill=tk.X, expand=tk.TRUE, side=tk.LEFT)
        input_dir_button = tk.Button(current_frame, text="...", command=self.on_browse_input)
        input_dir_button.pack(side=tk.LEFT, padx=PAD//2)
        # sorting
        current_frame = tk.Frame(input_frame, padx=PAD//2, pady=PAD//2)
        current_frame.pack(fill=tk.X, expand=tk.FALSE, side=tk.TOP)
        label = tk.Label(current_frame, text='sorting:', **LABEL_OPT)
        label.pack(fill=tk.X, expand=tk.FALSE, side=tk.LEFT)
        button = tk.Checkbutton(current_frame, text="numbering", variable=self.is_numbering_checked)
        button.pack(side=tk.LEFT)
        button = tk.Checkbutton(current_frame, text="flip", variable=self.is_flip_checked)
        button.pack(side=tk.LEFT)
        button = tk.Checkbutton(current_frame, text="backward verso", variable=self.is_reversed_checked)
        button.pack(side=tk.LEFT)
        # output
        output_frame = tk.Frame(settings_frame)
        output_frame.pack(fill=tk.BOTH, expand=tk.TRUE, side=tk.TOP)
        # output dir
        current_frame = tk.Frame(output_frame, padx=PAD//2, pady=PAD//2)
        current_frame.pack(fill=tk.X, expand=tk.FALSE, side=tk.TOP)
        label = tk.Label(current_frame, text='ouput:', **LABEL_OPT)
        label.pack(fill=tk.X, expand=tk.FALSE, side=tk.LEFT)
        output_dir_path = tk.Entry(current_frame, textvariable=self.output_dirpath)
        output_dir_path.pack(fill=tk.X, expand=tk.TRUE, side=tk.LEFT)
        output_dir_button = tk.Button(current_frame, text="...", command=self.on_browse_output)
        output_dir_button.pack(side=tk.LEFT, padx=PAD//2)
        # output pattern
        current_frame = tk.Frame(output_frame, padx=PAD//2, pady=PAD//2)
        current_frame.pack(fill=tk.X, expand=tk.FALSE, side=tk.TOP)
        label = tk.Label(current_frame, text='rename :', **LABEL_OPT)
        label.pack(fill=tk.X, expand=tk.FALSE, side=tk.LEFT)
        output_rename = tk.Entry(current_frame, justify=tk.RIGHT, textvariable=self.output_pattern)
        output_rename.pack(fill=tk.X, expand=tk.TRUE, side=tk.LEFT)
        output_dir_button = tk.Button(current_frame, text="?", command=None)
        output_dir_button.pack(side=tk.LEFT, padx=PAD//2)

        # list
        self.input_file_cols = ['original', 'renamed']
        self.input_file_view = ttk.Treeview(self, columns=self.input_file_cols)
        self.input_file_view.pack(fill=tk.BOTH, expand=tk.TRUE, side=tk.TOP, padx=PAD//2, pady=PAD//2)
        for i, col_name in enumerate(['#0'] + self.input_file_cols):
            self.input_file_view.heading(col_name, text=col_name, anchor=tk.W, command=self.sort_col_factory(i))

        # proceed
        current_frame = tk.LabelFrame(self, text='proceed', padx=PAD//2, pady=PAD//2)
        current_frame.pack(padx=PAD//2, pady=PAD//2, fill=tk.X, expand=tk.FALSE, side=tk.TOP)
        button = tk.Button(current_frame, text="inplace", command=self.on_proceed)
        button.pack(side=tk.RIGHT, padx=PAD//2, pady=PAD//2)
        button = tk.Button(current_frame, text="copy", command=self.on_proceed)
        button.pack(side=tk.RIGHT, padx=PAD//2, pady=PAD//2)

        # default values
        self.output_pattern.set(options['pattern'])
        self.is_numbering_checked.set(1)
        self.is_flip_checked.set(1)
        self.is_reversed_checked.set(1)
        self.column_sort.set(0)

    def sort_col_factory(self, i):
        return lambda: self.column_sort.set(i)

    def on_populate(self):
        self.populate()

    def on_browse_input(self):
        browse_dirpath = tk.filedialog.askdirectory(title="Select scanned directory",
                                                  initialdir=self.input_dirpath.get(),)
        if browse_dirpath:
            self.input_dirpath.set(browse_dirpath)
            self.populate()

    def on_browse_output(self):
        browse_dirpath = tk.filedialog.askdirectory(title="Select output directory",
                                                  initialdir=self.output_dirpath.get(),)
        if browse_dirpath:
            self.output_dirpath.set(browse_dirpath)

    def on_sort_original(self):
        self.column_sort.set('names')

    def on_option(self):
        self.populate()

    def on_proceed(self):
        rectoverso(self.input_dirpath.get(),
                   self.output_dirpath.get(),
                   self.output_pattern.get(),
                   self.is_numbering_checked.get(),
                   self.is_flip_checked.get(),
                   self.is_reversed_checked.get())

    def populate(self):
        # sort
        input_filepaths = populate_pages(self.input_dirpath.get())
        input_filepaths = sort_policy(input_filepaths,
                                      self.is_numbering_checked.get(),
                                      self.is_flip_checked.get(),
                                      self.is_reversed_checked.get())

        output_filepaths = get_output_filepaths(input_filepaths,
                                                self.output_dirpath.get(),
                                                self.output_pattern.get())
        # only life names
        if True:
            input_filepaths = (path.relpath(f, self.input_dirpath.get()) for f in input_filepaths)
            output_filepaths = (path.relpath(f, self.output_dirpath.get()) for f in output_filepaths)

        columns = [(p, i, o) for p, (i, o) in enumerate(zip(input_filepaths, output_filepaths))]

        # resort for display
        columns = sorted(columns, key=lambda x : x[self.column_sort.get()])

        # display
        self.input_file_view.delete(*self.input_file_view.get_children())
        for i, cols in enumerate(columns):
            self.input_file_view.insert('', 'end', text=cols[0], values=cols[1:])


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
