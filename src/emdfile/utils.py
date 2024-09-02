import h5py
from emdfile.classes import Metadata
from emdfile.classes.utils import _get_class, EMD_data_group_types
from uuid import uuid4

# read utilities - file level

def _get_EMD_rootgroups(filepath):
    """
    Returns a list of root groups in an EMD 1.0 file.
    """
    rootgroups = []
    with h5py.File(filepath,'r') as f:
        for key in f.keys():
            if 'emd_group_type' in f[key].attrs:
                if f[key].attrs['emd_group_type'] == 'root':
                    rootgroups.append(key)
    return rootgroups

def _is_EMD_file(filepath):
    """
    Returns True iff filepath points to a valid EMD 1.0 file.
    """
    # confirm that the file is an HDF5 file
    try:
        with h5py.File(filepath,'r') as f:
            pass
    except OSError:
        raise Exception(f"The file at {filepath} is not an HDF5 file!")
    # check for the 'emd_group_type'='file' attribute
    with h5py.File(filepath,'r') as f:
        try:
            assert('emd_group_type' in f.attrs.keys())
            assert('version_major' in f.attrs.keys())
            assert('version_minor' in f.attrs.keys())
            assert(f.attrs['emd_group_type'] == 'file')
            assert(f.attrs['version_major'] == 1)
            assert(f.attrs['version_minor'] == 0)
        except AssertionError:
            return False
    rootgroups = _get_EMD_rootgroups(filepath)
    if len(rootgroups)>0:
        return True
    else:
        return False

def _get_EMD_version(filepath, rootgroup=None):
    """
    Returns the version (major,minor,release) of an EMD file.
    """
    assert(_is_EMD_file(filepath)), "Error: not recognized as an EMD file"
    with h5py.File(filepath,'r') as f:
        v_major = int(f.attrs['version_major'])
        v_minor = int(f.attrs['version_minor'])
        if 'version_release' in f.attrs.keys():
            v_release = int(f.attrs['version_release'])
        else:
            v_release = 0
        return v_major, v_minor, v_release

def _get_UUID(filepath):
    """
    Returns the UUID of an EMD file, or if unavailable returns -1.
    """
    assert(_is_EMD_file(filepath)), "Error: not recognized as an EMD file"
    with h5py.File(filepath,'r') as f:
        if 'UUID' in f.attrs:
            return f.attrs['UUID']
    return -1

def _version_is_geq(current,minimum):
    """
    Returns True iff current version (major,minor,release) is greater than or equal to minimum."
    """
    if current[0]>minimum[0]:
        return True
    elif current[0]==minimum[0]:
        if current[1]>minimum[1]:
            return True
        elif current[1]==minimum[1]:
            if current[2]>=minimum[2]:
                return True
        else:
            return False
    else:
        return False


# read utilities - group and tree level

def _read_single_node(grp):
    """
    Determines the class type of the h5py Group `grp`, then
    instantiates and returns an instance of the class with
    this group's data and metadata
    """
    __class__ = _get_class(grp)
    data = __class__.from_h5(grp)
    return data

def _populate_tree(node,group,count=0):
    """
    `node` is a Node and `group` is its parallel h5py Group.
    Reads the tree underneath this nodegroup in the h5 file and adds it
    to the runtime tree underneath this node. Does *not* read `group`
    itself - this function grafts everything underneath `group` onto node

    Returns the number of new nodes added to the tree
    """
    keys = [k for k in group.keys() if isinstance(group[k],h5py.Group)]
    keys = [k for k in keys if 'emd_group_type' in group[k].attrs.keys()]
    keys = [k for k in keys if group[k].attrs['emd_group_type'] in \
        EMD_data_group_types]
    for key in keys:
        new_node = _read_single_node(group[key])
        count += 1
        node.force_add_to_tree(new_node)
        _populate_tree(
            new_node,
            group[key],
            count = count
        )
    return count

def _read_metadata(
    group,
    name
    ):
    """
    Returns a Metadata instance called name stored in the EMD node at group.
    Returns False otherwise.
    """
    try:
        grp_metadata = group['metadatabundle']
    except KeyError:
        return False
    try:
        metadata = Metadata.from_h5(grp_metadata[name])
        return metadata
    except KeyError:
        return False


# Write utilities

def _write_header(
    file
    ):
    from emdfile import _PROGRAM_NAME, _USER_NAME
    file.attrs.create("emd_group_type",'file')
    file.attrs.create("version_major",1)
    file.attrs.create("version_minor",0)
    file.attrs.create("UUID",str(uuid4()))
    file.attrs.create("authoring_program",_PROGRAM_NAME)
    file.attrs.create("authoring_user",_USER_NAME)

def _write_from_root(
    file,
    root,
    data,
    tree
    ):
    """ From an open h5py File with an EMD 1.0 header, adds a new root
    and data tree
    """
    # write the root
    rootgroup = _write_single_node(
        group = file,
        data = root,
    )
    rootgroup.attrs['emd_group_type'] = 'root'

    # write the rest
    if data is root:
        if tree is False:
            pass
        else:
            _write_tree(
                group=rootgroup,
                data=data
            )
    else:
        if tree is False:
            grp = _write_single_node(
                group = rootgroup,
                data = data
            )
        elif tree is True:
            grp = _write_single_node(
                group = rootgroup,
                data = data
            )
            _write_tree(
                group = grp,
                data = data
            )
        else:
            _write_tree(
                group = rootgroup,
                data = data
            )

def _write_single_node(
    group,
    data
    ):
    grp = data.to_h5(group)
    return grp

def _write_tree(
    group,
    data
    ):
    """ Writes the data tree underneath `data`; does not write `data`
    """
    for k in data._branch.keys():
        grp = _write_single_node(
            group = group,
            data = data._branch[k]
        )
        _write_tree(
            grp,
            data._branch[k]
        )

def _append_root_metadata(
    rootgroup,
    root,
    appendover
    ):
    # Determine if there is new group metadata
    if len(root._metadata)==0:
        return
    # Get file root metadata groups
    metadata_groups = []
    if "metadatabundle" not in rootgroup.keys():
        mdbundle_group = rootgroup.create_group('metadatabundle')
    else:
        mdbundle_group = rootgroup['metadatabundle']
        for k in mdbundle_group.keys():
            if "emd_group_type" in mdbundle_group[k].attrs.keys():
                if mdbundle_group[k].attrs["emd_group_type"] == "metadata":
                    metadata_groups.append(k)
    # loop
    for key in root._metadata:
        # if this group already exists
        if key in metadata_groups:
            # overwrite it
            if appendover:
                del(mdbundle_group[key])
                root._metadata[key].to_h5(mdbundle_group)
            # or skip it
            else:
                pass
        # otherwise, write it
        else:
            root._metadata[key].to_h5(mdbundle_group)
    return

def _validate_treepath(
    rootgroup,
    treepath
    ):
    """
    Accepts a file rootgroup and a runtime `treepath` string.
    If the treepath is not in the file, returns False.
    If the treepath is in the file, returns (grp, True) and
    if the treepath is one node beyond the file, returns (grp, False),
    where `grp` is the final h5py Group on treepath in the file tree.
    """
    grp_names = treepath.split('/')
    try:
        grp_names.remove('')
    except ValueError:
        pass
    group = rootgroup
    for i,name in enumerate(grp_names):
        if name not in group.keys():
            # catch for being one node beyond
            if i == len(grp_names)-1:
                return group, False
            return False
        group = group[name]
        try:
            assert(isinstance(group,h5py.Group))
        except AssertionError:
            return False
    return group, True

def _overwrite_single_node(
    group,
    data
    ):
    # get names
    groupname = group.name.split('/')
    name = groupname[-1]
    rootname = '/'+groupname[1]
    groupname = '/'+'/'.join(groupname[2:])

    # Validate
    assert(data.name == name), f"Can't overwrite - data/group names don't match: {data.name} != {name}"
    assert(groupname == data._treepath), f"Can't overwrite - data/group paths dont match: {group.name != data._treepath}"

    # Get parent group
    parentpath = data._treepath.split('/')
    parentpath = rootname+'/'.join(parentpath[:-1])
    parentgroup = group.file[parentpath]

    # Rename the old group
    parentgroup.move(name,"_tmp_"+name)

    # Write the new data 
    new_group = _write_single_node(
        parentgroup,
        data
    )

    # Copy the links
    keys = [k for k in group.keys() if "emd_group_type" in group[k].attrs.keys()]
    keys = [k for k in keys if group[k].attrs["emd_group_type"] in EMD_data_group_types]
    for key in keys:
        new_group[key] = group[key]

    # Remove the old group
    del(parentgroup["_tmp_"+name],group)

    # Return
    return new_group

def _append_branch(
    group,
    data,
    appendover
    ):
    groupkeys = [k for k in group.keys() if "emd_group_type" in group[k].attrs.keys()]
    # for each node under `data`...
    for key in data._branch.keys():
        d = data._branch[key]
        # ...if this node doesn't exist in the H5, do a simple write
        if d.name not in groupkeys:
            _write_single_node(
                group,
                d
            )
            _write_tree(
                group,
                d
            )
        # otherwise, overwrite or skip it, then call this fn again
        else:
            if appendover:
                next_node = _overwrite_single_node(
                    group[key],
                    d
                )
            else:
                next_node = group[key]
            _append_branch(
                next_node,
                d,
                appendover
            )
