# Write EMD 1.0 formatted HDF5 files.

import h5py
import numpy as np
from warnings import warn
from os.path import exists,basename
from os import remove
from emdfile.classes import Node, Root, Array, Metadata
from emdfile.classes.utils import EMD_data_group_types
from emdfile.utils import (_is_EMD_file, _get_EMD_rootgroups, _write_header,
    _write_from_root, _write_single_node, _write_tree, _append_root_metadata,
    _validate_treepath, _overwrite_single_node, _append_branch)


def write(
    filepath,
    data,
    mode = 'w',
    tree = True,
    emdpath = None,
    ):
    """
    Saves data to an .h5 file at filepath.

    Parameters
    ----------
    filepath : str
        Save path
    data : emdfile.Node instance
        The data
    mode : str
        Valid modes are write ('w','write'), overwrite ('o','overwrite'), append
        ('a','+','append'), and append-over ('ao','oa','o+','+o','appendover').
        Write mode writes a new file, and raises an exception if a file
        of this name already exists.  Overwrite mode deletes any file of
        this name that already exists and writes a new file. Append and
        appendover mode write a new file if no file of this name exists,
        or if a file of this name does exist, adds new data to the file.
        How new data is added to an existing file depends on the `data`,
        `emdpath`, and `tree` arguments. Both 'a' and 'ao' modes attempt to
        detemine the difference between the data passed and that present in the
        existing HDF5 file, adding any data not already in the H5 and either
        skipping ('a') or overwriting ('ao') existing data.
    tree : True or False or None
        assuming `data` is a node containing a downstream tree of nodes,
        `tree` determines how the downstream tree should be treated.  If True
        (default), the entire tree is saved. If False, only the node itself is
        saved. If None, the downstream tree is saved, but the `data` node itself
        is excluded.
    emdpath : str or None
        In append or append-over mode, indicates where in the existing HDF5
        file to graft the data.  Must be a '/' delimited string pointing to an
        existing node. Passing the `emdpath` argument automatically changes the
        mode to append if it was set to write or overwrite.
    """
    # parse mode
    writemode = ['w', 'write']
    overwritemode = ['o', 'overwrite']
    appendmode = ['a', '+', 'append']
    appendovermode = [ 'oa', 'ao', 'o+', '+o', 'appendover']
    allmodes = writemode + overwritemode + appendmode + appendovermode

    # emdpath implies append mode
    if emdpath is not None and mode not in appendovermode:
        mode = 'a'

    # validate `mode` and `tree` inputs
    er = f"unrecognized mode {mode}; mode must be in {allmodes}"
    assert(mode in allmodes), er
    if tree == 'noroot':
        warn("`tree = 'noroot'` is deprecated and will be removed in a future version. Use `tree = None` instead.")
        tree = None
    assert(tree in (True,False,None)), f"invalid value {tree} passed for `tree`"
    if mode in writemode:
        assert(not(exists(filepath))), "A file already exists at this destination; use append or overwrite mode, or choose a new file path."

    # validate `data` inputs, and handle non-Node `data` inputs
    # numpy array -> Array
    if isinstance(data, np.ndarray):
        root = Root(name='root')
        data = Array(name='np.array',data=data)
        root.add_to_tree(data)
    # dictionaries -> Metadata
    elif isinstance(data, dict):
        root = Root(name='root')
        md = Metadata(name='dictionary',data=data)
        root.metadata = md
        data = root
    # Metadata
    elif isinstance(data, Metadata):
        root = Root(name='root')
        root.metadata = data
        data = root
    # Lists and tuples
    elif isinstance(data, (list,tuple)):
        assert(all( [isinstance(x,(np.ndarray,dict,Node)) for x in data] )), \
            "can only save np.array, dictionary, or emd.Node objects"

        # sort items into roots, nodes, and (np.array/dict)s
        list_roots = []
        list_nodes = []
        list_others = []
        for x in range(len(data)):
            x = data.pop(0)
            if isinstance(x,Root):
                list_roots.append(x)
            elif isinstance(x,Node):
                list_nodes.append(x)
            else:
                list_others.append(x)

        # sort nodes+array/dicts into rooted and unrooted
        list_rooted_nodes = []
        list_unrooted_items = []
        for x in list_nodes:
            if x.root is None:
                list_unrooted_items.append(x)
            else:
                list_rooted_nodes.append(x)
        list_unrooted_items += list_others

        # place all unrooted items into a single root
        if len(list_unrooted_items) > 0:
            root_savedlist = Root(name = "root_savedlist")
            ind_ars = 0
            ind_dics = 0
            for x in list_unrooted_items:
                if isinstance(x,Node):
                    root_savedlist.tree(x)
                elif isinstance(x,np.ndarray):
                    ar = Array(
                        name = f"array_{ind_ars}",
                        data = x
                    )
                    root_savedlist.tree(ar)
                    ind_ars += 1
                else:
                    dic = Metadata(
                        name = f"dictionary_{ind_dics}",
                        data = x
                    )
                    root_savedlist.metadata = dic
                    ind_dics += 1
            list_roots.insert(0,root_savedlist)

        # sort rooted nodes, group nodes with the same roots
        # ensure only selected items from each root are saved
        # trees holding several selected nodes will be flattened
        dict_roots = {}
        if len(list_rooted_nodes) > 0:
            # list all roots, check for duplicate names
            for x in list_rooted_nodes:
                rcurr,rname = x.root,x.root.name
                if rname not in dict_roots.keys():
                    dict_roots[rname] = rcurr
                else:
                    assert(rcurr is dict_roots[rname]), f"Two nodes have different roots with identical names! Try changing one of their names."
            # make new roots, replace in the dict
            for rname,rcurr in dict_roots.items():
                root_new = Root( name=rname )
                for m in rcurr.metadata.values():
                    root_new.metadata = m
                dict_roots[rname] = root_new

        # set mode to append
        if mode in writemode:
            mode = 'a'
        elif mode in overwritemode:
            if exists(filepath):
                remove(filepath)
            mode = 'a'
        else:
            pass

        # write roots
        for root in list_roots:
            write(
                filepath,
                root,
                tree = True,
                mode = mode
            )

        # write nodes
        for root in dict_roots.values():
            write(
                filepath,
                root,
                mode = mode
            )
        for item in list_rooted_nodes:
            write(
                filepath,
                item,
                emdpath = item.root.name,
                tree = False,
                mode = 'ao'
            )
        return


    # `data` should now be a Node!
    assert(isinstance(data,Node)), f"invalid type {type(data)} found for `data`"

    # get the root
    root = data._root
    if root is None:
        added_a_root = True
        root = Root(name=data.name+"_root")
        root.add_to_tree(data)
    else:
        added_a_root = False

    # overwrite mode - delete existing file
    if mode in overwritemode:
        if exists(filepath):
            remove(filepath)
        mode = 'w'

    # write a new file
    if mode in writemode or (
        mode in appendmode+appendovermode and not exists(filepath)):
        # open the file
        with h5py.File(filepath, 'w') as f:
            # write header
            _write_header(
                file = f
            )
            # write the file
            _write_from_root(
                file = f,
                root = root,
                data = data,
                tree = tree
            )

    # append to an existing file
    else:
        # validate that its an EMD file
        # get the rootgroups
        assert(_is_EMD_file(filepath)), "{filepath} does not point to an EMD 1.0 file"
        emd_rootgroups = _get_EMD_rootgroups(filepath)
        # open the file
        with h5py.File(filepath, 'a') as f:
            # if the root doesn't already exist and emdpath is None,
            # do a simple write as above
            if not(root.name in emd_rootgroups) and (emdpath is None):
                _write_from_root(
                    file = f,
                    root = root,
                    data = data,
                    tree = tree
                )
            # if the root doesn't already exist and emdpath is specified,
            # append the data to the target node
            elif not(root.name in emd_rootgroups):
                # parse emdpath
                if emdpath[0] == '/':
                    emdpath = emdpath[1:]
                l = emdpath.split('/')
                rootname = l[0]
                treepath = '/'.join(l[1:])
                # get the rootgroup
                assert(rootname in f.keys()), f"No root called {rootname} found - check your `emdpath`"
                rootgroup = f[rootname]
                # validate the emdpath
                # set target_grp to targeted EMD node
                where = _validate_treepath(
                    rootgroup,
                    treepath
                )
                if where is False:
                    raise Exception(f"No node found at {emdpath} in the EMD tree called {rootname} - check your `emdpath`")
                elif where[1] is False:
                    raise Exception(f"No node found at {emdpath} in the EMD tree called {rootname} - check your `emdpath`")
                else:
                    target_grp = where[0]

                # append to the tree...
                # ...if data is Root and tree is False
                if isinstance(data,Root) and (tree is False):
                    raise Exception("Incompatible inputs: if appending from a Root to an existing tree, `tree` can't be False.  Try changing `data` or `tree`.")
                # ...if data is Root and tree is True or None
                elif isinstance(data,Root):
                    _write_tree(
                        target_grp,
                        data
                    )
                # ...if data is a Node and tree is False
                elif tree is False:
                    _write_single_node(
                        target_grp,
                        data
                    )
                # ...if data is a Node and tree is True
                elif tree is True:
                    target_grp = _write_single_node(
                        target_grp,
                        data
                    )
                    _write_tree(
                        target_grp,
                        data
                    )
                # ...if data is a Node and tree is None
                else:
                    _write_tree(
                        target_grp,
                        data
                    )

            # if the root does exist and emdpath is None,
            # peform diffmerge A
            elif emdpath is None:
                # choose how to handle conflicts
                appendover = True if mode in appendovermode else False
                # get the rootgroup
                rootgroup = f[root.name]
                # compare/append root metadata
                _append_root_metadata(
                    rootgroup = rootgroup,
                    root = root,
                    appendover = appendover
                )
                # choose behavior and write...
                if data is root:
                    # ...if the data is the root
                    if tree is True:
                        _append_branch(
                            rootgroup,
                            data,
                            appendover
                        )
                    else:
                        pass
                else:
                    where = _validate_treepath(
                        rootgroup,
                        data._treepath
                    )
                    # ...if the datapath is not in the H5 path
                    if where is False:
                        raise Exception("The data passed can't be added to it's corresponding H5 tree - check that the data's `_treepath` is present in the existing EMD file")
                    else:
                        where,inside = where
                        # ...if the datapath is in the H5 path
                        if inside is True:
                            if tree is True:
                                if appendover:
                                    next_node = _overwrite_single_node(
                                        where,
                                        data
                                    )
                                else:
                                    next_node = where
                                _append_branch(
                                    next_node,
                                    data,
                                    appendover
                                )
                            elif tree is False:
                                if appendover:
                                    next_node = _overwrite_single_node(
                                        where,
                                        data
                                    )
                                else:
                                    pass
                            else:
                                _append_branch(
                                    where,
                                    data,
                                    appendover
                                )
                        # ...if the datapath is one node beyond the H5 path
                        else:
                            if tree is True:
                                new_node = _write_single_node(
                                    where,
                                    data
                                )
                                _write_tree(
                                    new_node,
                                    data
                                )
                            elif tree is False:
                                _write_single_node(
                                    where,
                                    data
                                )
                                pass
                            else:
                                _write_tree(
                                    where,
                                    data
                                )

            # if the root does exist and emdpath is specified,
            # peform diffmerge B
            else:
                # choose how to handle conflicts
                appendover = True if mode in appendovermode else False
                # parse emdpath
                if emdpath[0] == '/':
                    emdpath = emdpath[1:]
                l = emdpath.split('/')
                rootname = l[0]
                treepath = '/'.join(l[1:])
                # get the rootgroup
                rootgroup = f[root.name]
                # validate the emdpath
                # set target_grp to targeted EMD node
                where = _validate_treepath(
                    rootgroup,
                    treepath
                )
                if where is False:
                    raise Exception(f"No node found at {emdpath} in the EMD tree called {rootname} - check your `emdpath`")
                elif where[1] is False:
                    raise Exception(f"No node found at {emdpath} in the EMD tree called {rootname} - check your `emdpath`")
                else:
                    target_grp = where[0]
                # compare/append root metadata
                _append_root_metadata(
                    rootgroup = rootgroup,
                    root = root,
                    appendover = appendover
                )

                # choose behavior and write...
                # ...if the data is the root
                if data is root:
                    # Confirm that the target node is downstream of the root...
                    assert(rootgroup.__contains__(target_grp.name)), "Specified target node not found in the EMD file - check your emdpath."
                    # get the path from source to target, then
                    # move `data` to the target node point
                    path_to_target = target_grp.name.replace(rootgroup.name,'')[1:]
                    try:
                        data = data.tree(path_to_target)
                    except AssertionError:
                        raise Exception("Append failure - the target EMD node exists downstream of the source EMD node, however the target is not present in the corresponding runtime tree")
                    # write
                    if appendover and tree in (True,False):
                        target_grp = _overwrite_single_node(
                            target_grp,
                            data
                        )
                    if tree in (True,None):
                        _append_branch(
                            target_grp,
                            data,
                            appendover
                        )
                # ...if the data is a node...
                else:
                    # validate the source node path
                    where = _validate_treepath(
                        rootgroup,
                        data._treepath
                    )
                    # ...if the source node is not in the H5
                    if where is False:
                        raise Exception("The data passed can't be appended to it's corresponding H5 tree - the source runtime node can't be matched to the existing tree")
                    else:
                        source_grp,inside = where

                        # ...if the source node is one node beyond the H5
                        if inside is False:
                            # ...if it is one node past the targetted node, write
                            if source_grp.name == target_grp.name:
                                if tree in (True,None):
                                    _append_branch(
                                        target_grp,
                                        data,
                                        appendover
                                    )
                                else:
                                    _write_single_node(
                                        target_grp,
                                        data
                                    )
                            # ...otherwise, raise an Exception
                            else:
                                raise Exception("The data passed can't be added to it's corresponding H5 tree - check that the data's `.tree()` path is present in the existing EMD file")

                        # ...if the source node is in inside the H5
                        else:
                            # ...if the source node is the target node, write
                            if source_grp.name == target_grp.name:
                                if appendover and tree in (True,False):
                                    target_grp = _overwrite_single_node(
                                        target_grp,
                                        data
                                    )
                                if tree in (True,None):
                                    _append_branch(
                                        target_grp,
                                        data,
                                        appendover
                                    )
                            # ...if the source node is one node downstream of the target, write
                            elif basename(source_grp.name) in list(target_grp.keys()):
                                target_grp = source_grp
                                if appendover and tree in (True,False):
                                    target_grp = _overwrite_single_node(
                                        target_grp,
                                        data
                                    )
                                if tree in (True,None):
                                    _append_branch(
                                        target_grp,
                                        data,
                                        appendover
                                    )
                            # ...if the target node is downstream of the source node...
                            elif source_grp.__contains__(target_grp.name):
                                # get the path from source to target, then
                                # move `data` to the target node point
                                path_to_target = target_grp.name.replace(source_grp.name,'')[1:]
                                try:
                                    data = data.tree(path_to_target)
                                except AssertionError:
                                    raise Exception("Append failure - the target EMD node exists downstream of the source EMD node, however the target is not present in the corresponding runtime tree")
                                # write
                                if appendover and tree in (True,False):
                                    target_grp = _overwrite_single_node(
                                        target_grp,
                                        data
                                    )
                                if tree in (True,None):
                                    _append_branch(
                                        target_grp,
                                        data,
                                        appendover
                                    )
                            # ...otherwise raise an exception
                            else:
                                raise Exception("Append failure - target node may not be downstream of source node.  Check the emdpath and the runtime data tree.")

    # if a root was added, remove it
    if added_a_root:
        data._root = None

    # end
    pass

