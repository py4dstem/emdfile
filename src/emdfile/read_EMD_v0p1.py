# Read EMD v0.1 files

from pathlib import Path

import h5py
from emdfile.classes import Array

verbose = False

class emd_v0p1:
    
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
                if verbose:
                    print(f'{name} is EMDgroup')
                self.emds.append(obj)
    
    def _is_EMD_v0p1(self):
        if self.file_hdl.attrs['version_major'] == 0 and self.file_hdl.attrs['version_minor'] == 1:
            return True
        else:
            return False
        
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
    
    ans = []
    emd0 = None
    
   
    # determine if the file is EMD 1.0
    # if not, try reading it as an EMD 0.1
    #if not _is_EMD_file(filepath):
    #    read_EMD_v0p1(filepath)

    # TODO
    # walk the filetree, look for, and load an EMD 0.1 group
    with emd_v0p1(filepath) as emd0:

#         print('Available emds:', emd0.emds)
        # if no EMD 0.1 group is found, or if it is unreadable, raise an exception
        if len(emd0.emds) < 1:
            raise Exception("No EMD 0.1 groups found!")
        
        print('avail emds', emd0.emds)
        
        # read in the groups
        for emd_group in emd0.emds:
            data = emd_group['data'][:]
            
            dims = []
            dim_units = []
            dim_names = []
            for ii in range(data.ndim):
                cur_dim = emd_group[f'dim{ii+1}']
                dims.append(cur_dim[:])
                dim_units.append(cur_dim.attrs['units'][:])
                dim_names.append(cur_dim.attrs['name'][:])
            
            # TODO
            # put the data into an Array
#             ans = Array(
#                 data = data[:],
#                 name = emd_group.name,
#                 units = None,
#                 dims = dims,
#                 dim_units = dim_units,
#                 dim_names = dim_names,
#             )
            ans.append(data)

    return ans

