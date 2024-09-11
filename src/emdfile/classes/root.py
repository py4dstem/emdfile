from emdfile.classes import Node

class Root(Node):
    """
    Root nodes are identical to Node instances, except that the .root property
    points to this root itself.

    EMD trees must begin with a Root, and tree building will raise an Exception
    if no root is present. Node's with roots are protected: they can't be removed
    or added to another tree unless a graft, cut, or force_add operation is used.

    Root metadata is handled uniquely. Write operations include root metadata
    with any other data written from a tree, even if only a subset of the tree is
    written. When cutting a branch from a tree, the branch is removed and placed
    in a new root, thereby creating a new tree; the old root metadata may be
    included, excluded, or copied to the new root. Inclusion means the new root
    will contain pointers to the same metadata collections; copying means new
    collections with the same information will be generated and stored in the
    new root. When grafting a branch from one tree to another, metadata from the
    incoming branch's root can be included, excluded, or copied into the
    recieving root's metadata. Conflicting metadata collections may be skipped or
    overwritten. Conflicts are evaluated at the level of Metadata objects, which
    represent named collections of metadata, and are not evaluated at the level
    of individual items of metadata.
    """
    _emd_group_type = 'root'
    def __init__(self,name='root'):
        Node.__init__(self,name=name)
        self._treepath = ''
        self._root = self
