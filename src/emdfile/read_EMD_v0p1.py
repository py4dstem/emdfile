# Read EMD v0.1 files

from pathlib import Path

import h5py
from emdfile.classes import Array
from emdfile import Root

class emd_v0p1:
    """A class used to find data and metadata in emd v0.1 files."""
    def __init__(self, filename):
        # necessary declarations in case something goes bad
        self.file_hdl = None
        self.emds = []  # list of HDF5 groups with emd_data_type type 0.1
        # check filename type, change to pathlib.Path
        if isinstance(filename, str):
            filename = Path(filename)
        elif isinstance(filename, Path):
            pass
        else:
            raise TypeError('Filename is supposed to be a string or pathlib.Path or file object')

        # try opening the file
        try:
            self.file_hdl = h5py.File(filename, 'r')
        except:
            print('Error opening file for readonly: "{}"'.format(filename))
            raise

        self.file_hdl.visititems(self._is_emd_group)

    def __del__(self):
        self.file_hdl.close()

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.__del__()
        return None

    def _is_emd_group(self, name, obj):
        """Checks if a HDF5 item (group or dataset) is a emd v0.1 group. This is used in h5py.visititems."""
        if isinstance(obj, h5py.Group):
            if 'emd_group_type' in obj.attrs and obj.attrs['emd_group_type'] == 1:
                self.emds.append(obj)


def read_EMD_v0p1(
    filepath,
    verbose = True
    ):
    """
    File reader for EMD 0.1 files. Returns the data as emd v1.0 files.

    Args:
        filepath (str or Path): the file path
        verbose (bool): Extra output for debugging
    Returns:
        (emdfile.Array) the data
    """

    if isinstance(filepath, str):
        filepath = Path(filepath)

    root = Root(name=filepath.name)  # name is optional
    emd0 = None

    # walk the filetree, look for, and load an EMD 0.1 group
    with emd_v0p1(filepath) as emd0:

        # if no EMD 0.1 group is found, or if it is unreadable, raise an exception
        if len(emd0.emds) < 1:
            raise Exception("No EMD 0.1 groups found!")

        if verbose:
            print('available emds', emd0.emds)

        # read in the groups
        for emd_group in emd0.emds:
            data = emd_group['data'][:]

            dims = []
            dim_units = []
            dim_names = []
            for ii in range(data.ndim):
                cur_dim = emd_group[f'dim{ii+1}']
                dims.append(cur_dim[:])
                dim_units.append(cur_dim.attrs['units'])
                dim_names.append(cur_dim.attrs['name'])

            # Put the data into an emdfile.Array
            arr = Array(
                data = data[:],
                name = emd_group.name.split('/')[-1],
                units = None,
                dims = dims,
                dim_units = dim_units,
                dim_names = dim_names,
            )

            # Add the Array to the Root
            root.tree(arr)
    if len(emd0.emds) == 1:
        return arr
    elif len(emd0.emds) > 1:
        return root
