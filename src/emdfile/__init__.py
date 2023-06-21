

# classes

from emdfile.classes import (
    Metadata,
    Node,
    Root,
    Array,
    PointList,
    PointListArray,
    Custom
)





# header hooks

_PROGRAM_NAME = 'emdfile'
_USER_NAME = ''
def set_author(author):
    """ Accepts a string, which will be written to the "authoring_user" field in any EMD file headers
        written during this Python session
    """
    global _USER_NAME
    _USER_NAME = author





# read/write

from emdfile.read import (
    read,
    print_h5_tree,
    _is_EMD_file,
    _get_EMD_version,
    _version_is_geq,
    _read_metadata
)
from emdfile.write import write as save




# version

from emdfile.version import __version__





# n-dimensional progress bar

from emdfile.tqdmnd import tqdmnd




# test paths

from os.path import dirname,join
_TESTPATH = join(join(dirname(__file__), "../.."), "test/unit_test_data")




