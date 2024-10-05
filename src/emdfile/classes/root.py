from emdfile.classes import Node

class Root(Node):
    """
    A Root is a Node with its .root property pointing to itself.
    EMD trees must begin with a Root, and tree building operations will raise an
    Exception if no root is present. Once a node is added to a tree, it can't be
    removed or added to another tree unless a graft, cut, or force_add operation
    is used.

    A Root instance's metadata is considered associated with all nodes in its
    tree, and any write operation emanating from this tree will include its root
    metadata.  Cut and merge node.tree include several handling options for root
    metadata - see those docstrings for details.
    """
    _emd_group_type = 'root'
    def __init__(self,name='root'):
        Node.__init__(self,name=name)
        self._treepath = ''
        self._root = self
