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


def sort_lexicographical(file_list):
    """
    sort in lexicographical order (windows explorer should do that)
    :param file_list:
    :return:
    """
    return sorted(file_list)


def sort_brother_numbering(file_list):
    """
    :param file_list:
    :return:
    """
    brother_numbering_template = re.compile(r'_(?P<date>\d{8})(_(?P<num>\d+))?')

    def get_brother_number(filepath):
        return int(brother_numbering_template.search(filepath).groupdict()['num'] or '1')

    return sorted(file_list, key=get_brother_number)


def sort_flip_recto_verso(file_list):
    """
    just swap even and odd pages, like in the example below :
    in: [ 'A (2).jpg', 'A.jpg', 'B (2).jpg', 'B.jpg', ...]
    out: [ 'A.jpg', 'A (2).jpg', 'B.jpg', 'B (2).jpg', ...]

    :param file_list:
    :return: sorted file list
    """
    odds = file_list[::2]
    evens = file_list[1::2]
    swapped = [page for evens_odds in zip(evens, odds) for page in evens_odds]
    if not len(odds) == len(evens):
        assert len(odds) == len(evens) - 1
        swapped.append(odds[-1])
    return swapped


def sort_backward_verso(file_list):
    """
    just reverse order (backward) of odd pages only, like in the example below :
    in: [1,6,3,4,5,2]
    out: [1,2,3,4,5,6]

    :param file_list:
    :return: sorted file list
    """
    # allocate
    reorderd_list = [None] * len(file_list)
    # keep even pages untouched
    reorderd_list[::2] = file_list[::2]
    # reveres order of odd pages
    reorderd_list[1::2] = list(reversed(file_list[1::2]))
    return reorderd_list


def sort_policy(filepaths, sorting_numbering, sort_flip_sheets, sort_backward_verso):
    """
    apply all sorting in the correct order.
    :param filepaths:
    :param sorting_numbering:
    :param sort_flip_sheets:
    :param sort_backward_verso:
    :return:
    """
    filepaths = sort_lexicographical(filepaths)
    if sorting_numbering:
        filepaths = sort_brother_numbering(filepaths)
    if sort_flip_sheets:
        filepaths = sort_flip_recto_verso(filepaths)
    if sort_backward_verso:
        filepaths = sort_backward_verso(filepaths)
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
