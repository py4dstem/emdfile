# Read EMD v0.1 files

import h5py
import pathlib
from os.path import exists, splitext, basename, dirname, join
from typing import Union, Optional
import warnings




def read_EMD_v0p1(
    filepath,
    ):
    """
    File reader for EMD 0.1 files.

    Args:
        filepath (str or Path): the file path

    Returns:
        (Array) the data
    """

    # determine if the file is EMD 1.0
    # if not, try reading it as an EMD 0.1
    if not _is_EMD_file(filepath):
        read_EMD_v0p1(filepath)

    # TODO
    # walk the filetree, look for, and load an EMD 0.1 group
    with h5py.File(fp,'r') as f:
        pass

    # if no EMD 0.1 group is found, or if it is unreadable, raise an exception
    raise Exception("No EMD 0.1 groups found!")

    # TODO
    # put the data into an Array
    #ans = Array(
    #    data = data,
    #    name = ,
    #    units = ,
    #    dims = ,
    #    dim_units = ,
    #    dim_names = ,
    #)

    # return
    return ans

