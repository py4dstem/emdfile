# Read functions

import h5py
import pathlib
from os.path import exists, join
from typing import Union, Optional
from emdfile import Root
from emdfile.read_EMD_v0p1 import read_EMD_v0p1
from emdfile.utils import (
    _is_EMD_file,
    _get_EMD_version,
    _get_EMD_rootgroups,
    _populate_tree,
    _read_single_node,
)

def read(
    filepath,
    emdpath: Optional[str] = None,
    tree: Optional[Union[bool,str]] = True,
    **legacy_options,
    ):
    """
    A file reader for EMD (Berkeley) files.

    Both the current EMD 1.0 file format and the older EMD 0.1 format are
    supported. The specifications can be found at https://emdatasets.com/format/
    and https://emdatasets.com/emd-0-1/, respectively.

    To read a subset of a file, specify a target node with the ``emdpath``
    argument and the recursion behavior with the ``tree`` argument. For files
    containing a single EMD tree, read the entire file by passing no arguments
    beyond the filepath.  For files containing multiple EMD trees, trees must
    be read one and a time - specify a tree of interest by passing its root to
    ``emdpath``.

    Parameters
    ----------
    filepath : str or Path
        the file path
    emdpath : str or None
        to read a subset of the file, set this argument to the HDF5 goup path of
        a target node in the file. If None and the file contains a single root,
        that root is set as the target node.  If None and the file contains
        multiple roots, a list of rootnames is returned and a warning raised;
        target the tree associated with a single root by passing its name to this
        argument.  To target any other node, specify its path using ``'/'``
        delimiters.
    tree : True or False or None
        indicates what data should be loaded.  If True reads the entire tree
        starting at and downstream of the target node.  If False,
        read the target node only.  If None, return the entire tree downstream of but
        excluding the target node.  Note that if ``emdpath`` points to a root
        node, setting ``tree`` to None or True are equivalent - both return the
        whole data tree.

    Returns
    -------
    Root or Node or Metadata
    """
    # validate filepath
    assert(isinstance(filepath, (str,pathlib.Path) )), f"filepath must be a string or Path, not {type(filepath)}"
    assert(exists(filepath)), f"specified filepath '{filepath}' was not found on the filesystem"

    # determine if the file is EMD 1.0
    # if not, try reading it as an EMD 0.1
    if not _is_EMD_file(filepath):
        try:
            print(f"This file is not an EMD v1.0 file - attempting to read as an EMD v0.1...")
            ans = read_EMD_v0p1(filepath)
            return ans
        except:
            raise Exception(f"The file at '{filepath}' is not recognized as an EMD file!")
    # get the version
    v = _get_EMD_version(filepath)

    # determine `emdpath` if it was left as None
    if emdpath is None:
        rootgroups = _get_EMD_rootgroups(filepath)
        if len(rootgroups) == 0:
            raise Exception("No root groups found! This error should never occur! You're amazing! You've broken the basic laws of logic, reason, and thermodynamics itself!!")
        elif len(rootgroups) == 1:
            emdpath = rootgroups[0]
        else:
            print("Multiple root groups detected - please specify the `emdpath` argument. Returning a list of root group names.")
            return rootgroups

    # parse the root and tree paths
    p = emdpath.split('/')
    if '' in p:
        p.remove('')
    rootpath = p[0]
    treepath = '/'.join(p[1:])

    # Open the h5 file...
    with h5py.File(filepath,'r') as f:
        # Find the root group
        assert(rootpath in f.keys()), f"Error: root group {rootpath} not found"
        rootgroup = f[rootpath]
        # Find the node of interest
        group_names = treepath.split('/')
        nodegroup = rootgroup
        if len(group_names)==1 and group_names[0]=='':
            pass
        else:
            for name in group_names:
                assert(name in nodegroup.keys()), f"Error: group {name} not found in group {nodegroup.name}"
                nodegroup = nodegroup[name]
        # Read the root
        root = Root.from_h5(rootgroup)
        # if this is all that was requested, return
        if nodegroup is rootgroup and tree is False:
                return root

        # Read...
        # ...if the whole tree was requested
        if nodegroup is rootgroup and tree in (True,'branch'):
            # build the tree
            n = _populate_tree(root,rootgroup)
            # return...
            if n == 1:
                # ...if there's one node, return it
                key = list(root._branch.keys())[0]
                node = root.tree(key)
            elif n == 0 and len(root.metadata) == 1:
                # ...if there's no nodes and one dictionary,
                # return it
                key = list(root.metadata.keys())[0]
                node = root.metadata[key]
            else:
                # ...otherwise, return the root
                node = root
        # ...if a single node was requested
        elif tree is False:
            # read the node
            node = _read_single_node(nodegroup)
            # build the tree and return
            root.force_add_to_tree(node)
        # ...if a branch was requested
        elif tree is True:
            # read source node and add to tree
            node = _read_single_node(nodegroup)
            root.force_add_to_tree(node)
            # build the tree
            _populate_tree(node,nodegroup)
        # ...if `tree == None`
        elif tree is None or tree=='branch':
            # build the tree
            _populate_tree(root,nodegroup)
            node = root
        else:
            raise Exception(f"Invalid argument for `tree` {tree}; must be True, False, or None")

    # Return
    return node

# Print the HDF5 filetree to screen
def print_h5_tree(filepath, show_metadata=False):
    """
    Prints the contents of an h5 file from a filepath.
    """
    with h5py.File(filepath,'r') as f:
        print('/')
        _print_h5pyFile_tree(f, show_metadata=show_metadata)
        print('\n')

def _print_h5pyFile_tree(f, tablevel=0, linelevels=[], show_metadata=False):
    """
    Prints the contents of an h5 file from an open h5py File instance.
    """
    if tablevel not in linelevels:
        linelevels.append(tablevel)
    keys = [k for k in f.keys() if isinstance(f[k],h5py.Group)]
    if not show_metadata:
        keys = [k for k in keys if k != 'metadatabundle']
    N = len(keys)
    for i,k in enumerate(keys):
        string = ''
        string += '|' if 0 in linelevels else ' '
        for idx in range(tablevel):
            l = '|' if idx+1 in linelevels else ' '
            string += '   '+l
        print(string+'---'+k)
        if i == N-1:
            linelevels.remove(tablevel)
        _print_h5pyFile_tree(
            f[k],
            tablevel=tablevel+1,
            linelevels=linelevels,
            show_metadata=show_metadata)
    pass
