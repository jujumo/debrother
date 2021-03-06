from tkinter import filedialog, messagebox
import tkinter as tk
from tkinter import ttk
import os.path as path
import configparser
from core import populate_pages, sort_policy, get_output_filepaths, rectoverso
import logging
import sys
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG)


class Config:
    def __init__(self, filepath, **kwargs):
        self._filepath = filepath
        self._data = kwargs
        assert all(kw in kwargs for kw in ['input', 'output', 'pattern'])

    def set_default(self):
        self._data['input'].set('./')
        self._data['output'].set('./')
        self._data['pattern'].set('{page:03}')

    def load(self):
        logger.info(f'loading from {self._filepath}')
        config = configparser.ConfigParser()
        config.read(self._filepath)
        for k in self._data:
            value = config['DEFAULT'].get(k)
            if value:
                self._data[k].set(value)

    def save(self):
        logger.info(f'saving to {self._filepath}')
        config = configparser.ConfigParser()
        for k in self._data:
            val = self._data[k].get()
            config['DEFAULT'][k] = str(val)
        with open(self._filepath, 'w') as configfile:
            config.write(configfile)


class DebrotherMainWindow(tk.Frame):
    def __init__(self, master, **args):
        self.master = master
        super().__init__(self.master, padx=10, pady=10)
        self.master.title('debɹother')
        self.pack(fill=tk.BOTH, expand=tk.TRUE)
        master.protocol("WM_DELETE_WINDOW", lambda: self.quit())

        master.geometry("600x800")
        # VARs
        self.input_dirpath = tk.StringVar()
        self.output_dirpath = tk.StringVar()
        self.output_pattern = tk.StringVar()
        self.is_numbering_checked = tk.IntVar()
        self.is_flip_checked = tk.IntVar()
        self.is_reversed_checked = tk.IntVar()
        self.do_delete_checked = tk.IntVar()
        self.column_sort = tk.IntVar()
        self.status = tk.StringVar()

        # config
        self._config = Config(
            args['config'],
            input=self.input_dirpath,
            output=self.output_dirpath,
            pattern=self.output_pattern,
            numbering=self.is_numbering_checked,
            flip=self.is_flip_checked,
            reversed=self.is_reversed_checked,
            move=self.do_delete_checked,
        )
        self._config.set_default()
        self._config.load()

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
        self.input_dirpath_entry = tk.Entry(current_frame, textvariable=self.input_dirpath)
        self.input_dirpath_entry.pack(fill=tk.X, expand=tk.TRUE, side=tk.LEFT)
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
        self.output_rename_entry = tk.Entry(current_frame, justify=tk.RIGHT, textvariable=self.output_pattern)
        self.output_rename_entry.pack(fill=tk.X, expand=tk.TRUE, side=tk.LEFT)
        output_dir_button = tk.Button(current_frame, text="?", command=self.on_rename_help)
        output_dir_button.pack(side=tk.LEFT, padx=PAD//2)

        # list
        self.input_file_cols = ['page', 'original', 'renamed']
        self.input_file_view = ttk.Treeview(self, columns=self.input_file_cols)
        self.input_file_view.pack(fill=tk.BOTH, expand=tk.TRUE, side=tk.TOP, padx=PAD//2, pady=PAD//2)
        for i, col_name in enumerate(['#0'] + self.input_file_cols):
            self.input_file_view.heading(col_name, text=col_name, anchor=tk.W, command=self.sort_col_factory(i))
        # '#0' is special
        self.input_file_view.heading('#0', text='#')
        self.input_file_view.column('#0', minwidth=40, width=40, stretch=tk.NO)

        # proceed
        current_frame = tk.LabelFrame(self, text='proceed', padx=PAD//2, pady=PAD//2)
        current_frame.pack(padx=PAD//2, pady=PAD//2, fill=tk.X, expand=tk.FALSE, side=tk.TOP)
        self.proceed_button = tk.Button(current_frame, text="copy", command=self.on_proceed)
        self.proceed_button.pack(side=tk.RIGHT, padx=PAD//2, pady=PAD//2)
        button = tk.Checkbutton(current_frame, text="delete originals", variable=self.do_delete_checked)
        button.pack(side=tk.RIGHT, padx=PAD//2, pady=PAD//2)

        # status
        current_frame = tk.Label(self, bd=1, relief=tk.SUNKEN, anchor=tk.W,
                                 textvariable=self.status, font=('arial', 16, 'normal'))
        current_frame.pack(fill=tk.X, expand=tk.FALSE, side=tk.TOP)

        # default value
        self.input_dirpath.trace("w", lambda a, b, c: self.on_option_change())
        self.output_pattern.trace("w", lambda a, b, c: self.on_option_change())
        self.is_numbering_checked.trace("w", lambda a, b, c: self.on_option_change())
        self.is_flip_checked.trace("w", lambda a, b, c: self.on_option_change())
        self.is_reversed_checked.trace("w", lambda a, b, c: self.on_option_change())
        self.do_delete_checked.trace("w", lambda a, b, c: self.on_option_change())
        self.column_sort.trace("w", lambda a, b, c: self.on_option_change())
        # force update on startup
        self.on_option_change()

    def quit(self):
        self._config.save()
        self.master.destroy()

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
            self.show_status('{} files listed'.format(len(self.input_file_view.get_children())))

    def on_browse_output(self):
        browse_dirpath = tk.filedialog.askdirectory(title="Select output directory",
                                                    initialdir=self.output_dirpath.get(),)
        if browse_dirpath:
            self.output_dirpath.set(browse_dirpath)

    def on_rename_help(self):
        usage = "\
        - `{index}`: is the page number (0-based numbering).\n\
        - `{page}`: is the page number (1-based numbering). \n\t\t(eg. `{page:03d}`),\n\
        - `{ext}`: the original file extension (without `.`),\n\
        - `{yyyy}`: the current year,\n\
        - `{mm}`: the current month (`{mm:02d}` to pad),\n\
        - `{dd}`: the current day (`{dd:02d}` to pad),\n\
        - `{original}`: the original full file path,\n\
        - `{filename}`: the original file name (without directory),\n\
        - `{basename}`: the original base file name (without directory nor extension).\n\
        "
        tk.messagebox.showinfo("Naming syntax", usage)

    def on_option_change(self):
        self.do_validate_options()
        self.do_refresh()

    def do_validate_options(self):
        everything_is_fine = True
        NOR = 'White'
        RED = '#FFA0A0'
        ORANGE = '#FFFFA0'

        # input path
        if path.isdir(self.input_dirpath.get()):
            self.input_dirpath_entry.config(background=NOR)
        else:
            self.input_dirpath_entry.config(background=RED)
            everything_is_fine = False

        # name syntax
        try:
            get_output_filepaths([r'sample\sample.png'], 'tmp', self.output_pattern.get())
            self.output_rename_entry.config(background=NOR)
        except (ValueError, KeyError, IndexError) as e:
            self.output_rename_entry.config(background=RED)
            everything_is_fine = False

        # proceed authorized
        self.proceed_button.config(state=tk.NORMAL if everything_is_fine else tk.DISABLED)

    def do_refresh(self):
        self.populate()

    def show_status(self, message):
        self.status.set(message)

    def show_error(self, message):
        self.show_status('Error: ' + message)
        tk.messagebox.showerror("Error", message)

    def on_proceed(self):
        try:
            rectoverso(self.input_dirpath.get(),
                       self.output_dirpath.get() or self.input_dirpath.get(),
                       self.output_pattern.get(),
                       self.is_numbering_checked.get(),
                       self.is_flip_checked.get(),
                       self.is_reversed_checked.get(),
                       self.do_delete_checked.get()
                       )
            self.show_status('success')
        except FileNotFoundError as e:
            self.show_error(str(e))
        finally:
            self.on_option_change()

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
            page_numbers = (f'{p+1:04}' for p, _ in enumerate(input_filepaths))
            input_filepaths = (path.relpath(f, self.input_dirpath.get()) for f in input_filepaths)
            output_filepaths = (path.relpath(f, self.output_dirpath.get()) for f in output_filepaths)

        columns = [(i, p, ip, op) for i, (p, ip, op) in enumerate(zip(page_numbers, input_filepaths, output_filepaths))]

        # resort for display
        columns = sorted(columns, key=lambda x : x[self.column_sort.get()])

        # display
        self.input_file_view.delete(*self.input_file_view.get_children())
        for i, cols in enumerate(columns):
            self.input_file_view.insert('', 'end', text=cols[0], values=cols[1:])
