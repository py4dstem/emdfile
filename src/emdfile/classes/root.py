from emdfile.classes import Node

class Root(Node):
    """
    Root nodes are identical to Node instances, except that the .root property
    points to this root itself.

    They are additionally treated differently by other functions in emdfile - in
    paticular, every EMD tree must begin with a Root instance. Root metadata is
    intended to represent metadata relevant to the entire tree, is also therefore
    treated specially - writing a node or branch downstream from the root to a
    file will still carry the root metadata with it, and nodes or branches that
    are cut or grafted from a tree will by default have root metadata carried
    with them as well.
    """
    _emd_group_type = 'root'
    def __init__(self,name='root'):
        Node.__init__(self,name=name)
        self._treepath = ''
        self._root = self
