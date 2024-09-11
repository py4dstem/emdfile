from emdfile.classes import Node

class Root(Node):
    """
    Root nodes are identical to Node instances, except that the .root property
    points to this root itself.

    EMD trees must begin with a Root, and tree building will raise an Exception
    if no root is present. Node's with roots are protected: they can't be removed
    or added to another tree unless a graft, cut, or force_add operation is used.

    Write operations include root metadata with any other data written from its
    tree, even if only a subset of the tree is written. Root data may be
    included, excluded, or copied to the new root when cutting a branch from a
    tree. Similarly when grafting, metadata from the incoming branch's root can be
    added, excluded, or copied into the recieving root's metadata. Conflicting
    metadata collections may be skipped or overwritten.
    """
    _emd_group_type = 'root'
    def __init__(self,name='root'):
        Node.__init__(self,name=name)
        self._treepath = ''
        self._root = self
