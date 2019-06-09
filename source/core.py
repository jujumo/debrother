import os
import os.path as path
import re
from shutil import copyfile
import logging


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


def sort_policy(filepaths, sorting_brother, sort_windows, sort_reversed):
    filepaths = sorted(filepaths)
    if sorting_brother:
        filepaths = sort_brother_pages(filepaths)
    if sort_windows:
        filepaths = sort_widnows_files(filepaths)
    if sort_reversed:
        filepaths = sort_reversed_verso(filepaths)
    return filepaths


def get_output_filepaths(filepaths, output_dirpath, output_pattern):
    input_infos_list = [{
        'original': filepath,
        'page': page,
        'filename': path.basename(filepath),
        'basename': path.splitext(path.basename(filepath))[0],
        'ext': path.splitext(path.basename(filepath))[1][1:],
    } for page, filepath in enumerate(filepaths)]
    output_filepath = path.join(output_dirpath, output_pattern)
    return [output_filepath.format(**infos) for infos in input_infos_list]


def rename_files(input_filepaths, output_filepaths):
    assert len(input_filepaths) == len(output_filepaths)

    # - copy into a temp location
    # - move to actual location
    # - delete input (if requested)
    # - if errors: roll back

    for src, dst in zip(input_filepaths, output_filepaths):
        logging.debug('rename:\n\tfrom: {i}\n\tto  : {o}'.format(i=src, o=dst))
        copyfile(src, dst)


def rectoverso(input_dirpath,
               output_dirpath,
               output_filepattern,
               sorting_brother=True,
               sort_windows=True,
               sort_reversed=True):
    input_filepath_list = populate_pages(input_dirpath)
    nb_files = len(input_filepath_list)
    logging.info('files to rename: {}.'.format(nb_files))

    input_filepath_list = sort_policy(input_filepath_list, sorting_brother, sort_windows, sort_reversed)
    output_filepath_list = get_output_filepaths(input_filepath_list, output_dirpath, output_filepattern)
    rename_files(input_filepath_list, output_filepath_list)
