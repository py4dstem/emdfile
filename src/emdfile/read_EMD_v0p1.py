# Read EMD v0.1 files

from pathlib import Path

import h5py
from emdfile.classes import Array

verbose = True

def _is_emd_group(name, obj):
    """Checks if a HDF5 item (group or dataset) is a emd v0.1 group. This is used in h5py.visititems."""
    if isinstance(obj, h5py.Group):
        if 'emd_group_type' in obj.attrs and obj.attrs['emd_group_type'] == 1:
            print(f'{name} is EMDgroup')
            emds.append(obj)
        else:
            print(f'{name} is regular group')
    elif isinstance(obj, h5py.Dataset):
        print(f'{name} is dataset')
    else:
        print(f'{name} is an unknown instance')


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
    
    ans = None
    
    # determine if the file is EMD 1.0
    # if not, try reading it as an EMD 0.1
    if not _is_EMD_file(filepath):
        read_EMD_v0p1(filepath)

    # TODO
    # walk the filetree, look for, and load an EMD 0.1 group
    emds = []
    with h5py.File(filepath, r) as emd0:
        emd0.visititems(_is_emd_group)
        if verbose:
            print(emds)

        # if no EMD 0.1 group is found, or if it is unreadable, raise an exception
        if len(emds < 1):
            raise Exception("No EMD 0.1 groups found!")
        
        # TODO
        # read in the groups
        for emd_group in emds:
            data = emd_group['data']
            
            dims = []
            for ii in range(data.ndim):
                dims.append(emd_group[f'dim{ii+1}'])
        
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

