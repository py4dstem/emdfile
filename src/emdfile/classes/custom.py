import h5py
from emdfile.classes.node import Node
from emdfile.classes.root import Root
from emdfile.classes.utils import _get_class

class Custom(Node):
    """
    """
    _emd_group_type = 'custom'
    def __init__(self,name='custom'):
        Node.__init__(self,name=name)

    # read
    @classmethod
    def _get_constructor_args(cls,group):
        """
        Takes an h5py Group corresponding to some EMD node, and returns a
        dictionary of arguments/values to pass to the corresponding class
        constructor.

        Classes inheriting from Custom are required to overwrite this method.
        See the Node class docstring for additional information. To retrieve
        all custom sub-nodes, use ._get_emd_attr_data. If metadata items
        are needed for instantiation, a Node can be created containing the
        metadata only using

            >>> _node = Node.from_h5(group)
        """
        raise Exception(f"Custom class {cls} needs a `_get_constructor_args` method!")

    def _get_emd_attr_data(self,group):
        """ Loops through h5 groups under group, finding and returning
        a {name:instance} dictionary of {attribute name : class instance}
        pairs from all 'custom_' subgroups
        """
        groups = [g for g in group.keys() if isinstance(group[g],h5py.Group)]
        groups = [g for g in groups if 'emd_group_type' in group[g].attrs.keys()]
        groups = [g for g in groups if group[g].attrs['emd_group_type'][:7]=='custom_']
        dic = {}
        for g in groups:
            name,grp = g,group[g]
            __class__ = _get_class(grp)
            data = __class__.from_h5(grp)
            dic[name] = data
        return dic

    # write
    def to_h5(self,group):
        """
        Creates a subgroup in `group` and writes this node into that group,
        including the group tags (emd_group_type, python_class), and the
        node's metadata.

        Additionally, for every attribute which yields a Node instance,
        writes that node to a new child group using it's class .to_h5 method.

        Parameters
        ----------
        group : h5py Group

        Returns
        -------
        (h5py Group) the new node's Group
        """
        # Construct the group and add metadata
        grp = Node.to_h5(self,group)
        # Add any attributes which are themselves emd nodes
        for k,v in vars(self).items():
            if isinstance(v,Node):
                if not isinstance(v,Root):
                    v.name = k
                    attr_grp = v.to_h5(grp)
                    attr_grp.attrs['emd_group_type'] = 'custom_' + \
                        attr_grp.attrs['emd_group_type']
        return grp
