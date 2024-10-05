import h5py
from emdfile.classes.node import Node
from emdfile.classes.root import Root
from emdfile.classes.utils import _get_class

class Custom(Node):
    """
    The purpose of Custom nodes is to support creation of new classes by
    composition of emdfile classes. To do so, create a class inheriting
    from Custom, then add attributes which are emdfile classes, for
    instance

        >>> class X(Custom):
        >>>     def __init__(self, name, asize, bsize):
        >>>         Custom.__init__(self, name=name)
        >>>         self.a = Array(np.ones((asize)),'a')
        >>>         self.b = Array(np.ones((bsize)),'b')

    For some X instance x, on write x.a and x.b will be saved, along with any
    other attributes pointing to Node instances.

    .. topic:: Downstream Integration

        See the Node docstring. Node-like attributes will be written to file by
        the Custom.to_h5 method, however, to ensure those attributes are correctly
        read the new class must modify the ._get_constructor_args and
        ._populate_instance methods.

        ._get_emd_attr_data provides access to node-like attributes, which it returns
        as a dictionary. So for class X above, we could use

            >>> @classmethod
            >>> def _get_constructor_args(cls, group):
            >>>     d = cls._get_emd_attr_data(group)
            >>>     args = {
            >>>         'a' : d['a'].shape,
            >>>         'b' : d['b'].shape
            >>>     }
            >>> return args

        to ensure the right arguments are passed to ``X.__init__``. If for some
        X instance x the x.a and x.b attribute data changed after
        instantiation but before it was written to disk, these will need to
        be populated, which can be accomoplished e.g. with

            >>> def _populate_instance(self, group):
            >>>     d = cls._get_emd_attr_data(group)
            >>>     self.a = d['a']
            >>>     self.b = d['b']
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
        all custom sub-nodes, use ._get_emd_attr_data. To retrieve to top
        level node metadata, use

            >>> md = Node.from_h5(group).metadata
        """
        raise Exception(f"Custom class {cls} needs a `_get_constructor_args` method!")

    def _populate_instance(self,group):
        """
        Run while reading an object from file after instantiation.

        Classes inheriting from Custom are required to overwrite this method.
        See the Node class docstring for additional information. To retrieve
        all custom sub-nodes, use ._get_emd_attr_data. To retrieve to top
        level node metadata, use

            >>> md = Node.from_h5(group).metadata
        """
        raise Exception(f"Custom class {cls} needs a `_populate_instance` method!")

    def _get_emd_attr_data(self,group):
        """
        Loops through h5 groups under group, finding and returning
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
        Calls Node.to_h5 to greate the group's node and write its metadata.
        Then writes every attribute yielding a Node instance using that
        node's .to_h5 method.

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
