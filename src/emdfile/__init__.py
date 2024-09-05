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
    """
    Accepts a string, which will be written to the "authoring_user" field in any
    EMD file headers written during this Python session
    """
    global _USER_NAME
    _USER_NAME = author
def set_program(program):
    """
    Accepts a string, which will be written to the "authoring_program" field in any
    EMD file headers written during this Python session
    """
    global _PROGRAM_NAME
    _PROGRAM_NAME = program

# read/write
from emdfile.read import read,print_h5_tree
from emdfile.read import print_h5_tree as printtree
from emdfile.write import write as save
from emdfile.utils import
    _is_EMD_file,
    _get_EMD_version,
    _version_is_geq,
    _get_UUID,
    _read_metadata
)

from emdfile.version import __version__ # version
from emdfile.tqdmnd import tqdmnd       # n-dimensional progress bar
from os.path import dirname,join
_TESTPATH = join(join(dirname(__file__), "../.."), "test/unit_test_data") # test paths

