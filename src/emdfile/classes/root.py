from emdfile.classes import Node

class Root(Node):
    """
    A Rode Node.
    """
    _emd_group_type = 'root'
    def __init__(self,name='root'):
        Node.__init__(self,name=name)
        self._treepath = ''
        self._root = self
