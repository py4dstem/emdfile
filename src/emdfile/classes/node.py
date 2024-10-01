import h5py
from os.path import basename
from typing import Optional
from emdfile.classes import Metadata
from emdfile.classes.utils import EMD_group_types, _get_class

class Node:
    """
    Base class for all EMD data object classes.

    Nodes include an interface for metadata and for their EMD data tree.
    The Node class itself does not include additional data; interface to
    data blocks therefore vary according to subclass (Array, PointList, etc.)

    Nodes also include their own read/write machinery. For downstream package
    integration - i.e. defining your own classes which inherit from emdfile
    classes - some modifications should be made for read and write operations
    to function correctly, discussed further below.

    Interface - Metdata and Data
    ----------------------------
    Metadata is found at

        >>> node.metadata

    and contains a dictionary of any number of Metadata instances.
    New metadata can be added using

        >>> node.metadata = Metadata(name='new_metadata', data={'item':1})

    which adds the new instance to the dictionary. See the Metadata docstring
    for additional information.  The node may have data depending on its subclass
    (Array, Pointlist, etc).

    Interface - EMD Trees
    ---------------------
    Nodes may be nested to form EMD trees, each of which must begin with a Root
    type node.

        >>> root = Root()
        >>> node1 = Node('node1')
        >>> root.tree(node1)

    creates the data tree

        root
          |---node1

    and

    .. code-block::

        ...
        node2 = Node('node2')
        node2.tree(node1)

    extends the tree to

        root
          |---node1
                |---node2

    Each node may contain its own data and metada. The

        >>> node.tree

    method enables displaying the tree, fetching another node, cutting a branch
    of the tree off to create a new tree, or grafting to/from another tree or
    subtree.  Usage includes

    .. code-block::

        node.tree()              show the tree downstream of this node
        node.tree(show=True)     show the full tree from the root node
        node.tree(show=False)    show from current node
        node.tree('path/to/node' return the node at the chosen location
        node.tree('/path/to/node specifiy the location starting from root
        node.tree(node)          add a child node; must be a Node instance
        node.tree(cut=True)      remove & return a branch; include root metadata
        node.tree(cut=False)     discard root metadata
        node.tree(cut='copy')    copy root metadata
        node.tree(graft=node)    remove & graft a branch; add new root metadata
        node.tree(graft=(node,True))  as above
        node.tree(graft=(node,False)) discard root metadata
        node.tree(graft=(node,'copy') copy new root metadata
        node.tree(graft=(node,'overwrite') add root metadata, overwrite conflicts
        node.tree(graft=(node,'copyover') copy root metadata, overwrite conflicts

    Showing the tree, retrieving or adding nodes, and cutting or grafting
    branches are also possible using the

    .. code-block::

        node.show_tree
        node.get_from_tree
        node.add_to_tree
        node.cut_from_tree
        node.graft

    methods.  See their docstrings for more info.
    The node root can be returned with

        >>> node.root

    Downstream Integration: Read & Write New Classes
    -------------------------------------------------
    For simple emdfile usage, this section is not required; the info that follows
    is needed for creating new classes inheriting from emdfile classes.

    Each Node contains

    .. code-block::

        node.to_h5
        node.from_h5

    methods, which write class instances to HDF5 files and generate new
    instances from appropriately formatted HDF5 groups, respectively.
    Guidelines for modifying these methods to create new classes follow.

    .to_h5
    ------
    This method will create a new HDF5 group and populate it with everything
    in node.metadata, top level group tags, and depending on the node class
    type, some data.  See the .to_h5 docstring for individual classes for
    description of that data.

    In cases where additional data needs to be written to the file, first ask
    - can the data be added to node.metadata?
    - can the data be included by inheriting a different emd node type (e.g.
      a custom node?)
    If the data can be easily included with these methods, no modification of
    .to_h5 should be needed.

    Otherwise, .to_h5 may be overwritten in your class.  The new method should
    begin

    .. code-block::

        def to_h5(self, group):
            '''describe the data being included '''
            grp = ParentClass.to_h5(self, group)
            ...

    where `ParentClass` is the class yours inherits from.  This will create the
    HDF5 group you're writing to and add all the data normally included. Add
    any additional required code, then conclude with

        >>> return grp

    .from_h5
    --------
    This file should not require modification in most instances. Instead, two
    helper methods it calls may be overwritten.  When run, node.from_h5 calls

    .. code-block::

        node._get_constructor_args
        node._populate_instance

    methods.  The first method retreives the arguments which will be passed to
    the class __init__ method from the HDF5 file.  The second method is called
    post-instantiation to perform any additional setup or modification of
    the new instance.

    node._get_constructor_args should be modified to return to arguments and
    values your class' __init__ method expects.  Your new method should begin

    .. code-block::

        @classmethod
        def _get_constructor_args(cls, group):

    and end

        >>> return args

    where `args` is a dictionary of the __init__ method inputs. You can use

        >>> parent_class_args = ParentClass._get_constructor_args(group)

    to retrieve standard argument/value pairs from the parent class. The output
    dictionary keys are identical to the input argument names for the class
    constructors, i.e. for Array instances the keys are 'data', 'name', 'units',
    'dims', 'dim_names', 'dim_units', and 'slicelabels'.

        >>> def _populate_instance(self, group):

    then add any code required to populate the new class instance with the
    required data.

    Downstream Integration: Hooking Dependent Packages
    ---------------------------------------------------
    If another Python module defines its own child classes of emdfile classes,
    add

        >>> _emd_hook = True

    as a global variable in its top-level namespace (e.g. in the top level
    __init__.py file). This ensures that emdfile is able to find the appropriate
    class definition when reading instances of this class from files.

    Extras
    ------
    Sometimes a class method will generate data which is itself an emdfile node.
    Decorating such a method with

        >>> @newnode

    modifies the mathod such that it (1) adds the new node to the tree of the
    generating node, and (2) adds metadata describing how that node was made.
    """
    _emd_group_type = 'node'
    def __init__(
        self,
        name: Optional[str] = 'node'
        ):
        self.name = name
        self._branch = Branch()   # enables accessing child groups
        self._treepath = None     # enables accessing parent groups
        self._root = None
        self._metadata = {}

    @property
    def root(self):
        return self._root
    @property
    def metadata(self):
        return self._metadata
    @metadata.setter
    def metadata(self,x):
        assert(isinstance(x,Metadata))
        self._metadata[x.name] = x
    @property
    def treekeys(self):
        return self._branch.keys()

    # displays top level contents of the node
    def __repr__(self):
        space = ' '*len(self.__class__.__name__)+'  '
        string = f"{self.__class__.__name__}( A Node called '{self.name}', containing the following top-level objects in its tree:"
        string += "\n"
        for k,v in self._branch.items():
            string += "\n"+space+f"    {k.ljust(24,' ')} \t ({v.__class__.__name__})"
        string += "\n)"
        return string

    def show_tree(self,root=False):
        """
        Display the object tree. If `root` is False, displays the branch
        of the tree downstream from this node, and if True, displays
        the full tree from the root node.
        """
        assert(isinstance(root,bool))
        if not root:
            self._branch.print()
        else:
            assert(self.root is not None), "Can't display an unrooted node from its root!"
            self.root._branch.print()

    def add_to_tree(self,node):
        """
        Add `node` to the current tree as a child of this node.
        Note that if `node` has a root, this will error out - in this case, use
        either .graft or .force_add_to_tree instead.
        """
        assert(isinstance(node,Node))
        assert(self.root is not None), "Can't add objects to an unrooted node. See the Node docstring for more info."
        assert(node.root is None), "Can't add a rooted node to a different tree.  Use `.tree(graft=node)` instead."
        node._root = self._root
        self._branch[node.name] = node
        node._treepath = self._treepath+'/'+node.name

    def force_add_to_tree(self,node):
        """
        Add `node` to the current tree as a child of this node, whether or not
        `node` has a root.  If it has no root, performs a simple add. If has a
        root, performs a graft, excluding the root metadata from `node`. Note
        that this means the branch downstream of `node` will also be moved to
        the current tree.
        """
        try:
            self.add_to_tree(node)
        except AssertionError:
            self.graft(node, merge_metadata=False)

    def get_from_tree(self,name):
        """
        Finds and returns the node from the current tree matching `name`, which
        must be a string with '/' delimiters between 'parent/child' nodes.
        Search from the current node, or from the root node if `name` begins
        with '/'. So

            >>> self.get_from_tree('x/y')

        fetches node 'y' which is under node 'x' which is under the current node,
        and

            >>> self.get_from_tree('/a/b')

        fetches node 'b' which is under 'a' which is under the root node.
        """
        if name == '':
            return self.root
        elif name[0] != '/':
            return self._branch[name]
        else:
            return self.root._branch[name]

    def _graft(self,node,merge_metadata=True):
        """
        Grafts a branch from one EMD tree onto another. The branch beginning at
        this node is moved onto `node`'s tree underneath `node`.

        For the reverse - i.e. grafting *to* this tree *from* another tree -
        use the .graft method.

        Parameters
        ----------
        node : Node
        merge_metadata : True, False, 'copy', or 'overwrite'
            Specifies how root metadata should be treated.  If True, adds the
            incoming root metadata to the receiving root, skipping entries that
            exist in both.  If False, adds no metadata. If "overwrite", entries
            existing in both scion and stock root metadata are overwritten.  If
            "copy", scion root metadata are copied to the stock root, passing
            conflicts. If "copyover", copies overwrite originals in conflicts.

        Returns
        -------
        (Node) the root node of the receiving tree
        """
        assert(self.root is not None), "Can't graft an unrooted node; try using .tree(add=node) instead."
        assert(node.root is not None), "Can't graft onto an unrooted node"

        # find upstream and root nodes
        old_root = self.root
        node_list = self._treepath.split('/')
        this_node = node_list.pop()
        treepath = '/'.join(node_list)
        upstream_node = self.get_from_tree(treepath)

        # if grafting from a non-root node
        if this_node != '':
            # remove connection from upstream to this node
            del(upstream_node._branch[this_node])
            # add to a new tree
            self._root = None
            node.add_to_tree(self)

        # if grafting from a root node
        else:
            # add objects one by one
            keys = list(upstream_node._branch.keys())
            for k in keys:
                n = upstream_node.tree(k)
                n._root = None
                node.add_to_tree(n)
                # remove upstream connections
                del(upstream_node._branch[k])

        # add old root metadata to this node
        assert(merge_metadata in [True,False,'copy','overwrite','copyover',])
        # no root metadata
        if merge_metadata is False:
            pass
        # add, don't overwrite
        elif merge_metadata is True:
            for key in old_root.metadata.keys():
                if key not in node.root.metadata.keys():
                    node.root.metadata = old_root.metadata[key]
        # add, overwrite
        elif merge_metadata == 'overwrite':
            for key in old_root.metadata.keys():
                node.root.metadata = old_root.metadata[key]
        # copy, don't overwrite
        elif merge_metadata == 'copy':
            for key in old_root.metadata.keys():
                node.root.metadata = old_root.metadata[key].copy()
        # copy, overwrite
        elif merge_metadata == 'copyover':
            for key in old_root.metadata.keys():
                if key not in node.root.metadata.keys():
                    node.root.metadata = old_root.metadata[key].copy()
        # return
        return node.root

    def graft(self,node,merge_metadata=True):
        """
        Grafts a branch from one EMD tree onto another. The branch beginning at
        `node` is moved onto this tree underneath this node.

        For the reverse - i.e. grafting *from* this tree *to* another tree -
        either use that tree's .graft method, or use this tree's ._graft.

        Parameters
        ----------
        node : Node
        merge_metadata : True, False, 'copy', or 'overwrite'
            Specifies how root metadata should be treated.  If True, adds the
            scion (incoming) root metadata to the stock (receiving) root,
            skipping entries that exist in both.  If False, adds no metadata.
            If "overwrite", entries existing in both scion and stock root
            metadata are overwritten.  If "copy", scion root metadata are
            copied to the stock root.

        Returns
        -------
        (Node) this tree's root node
        """
        return node._graft(
            self,
            merge_metadata=merge_metadata
        )

    def cut_from_tree(self,root_metadata=True):
        """
        Removes from the tree the branch beginning at this node, and returns it
        as a new tree.  A new root is created at the base of the tree named
        '{old_root_name}_cut_{this_node_name}'.

        Parameters
        ----------
        root_metadata : True, False, or 'copy'
            Specifies root metadata handling.  If True, adds metadata from the
            original tree root to the new root.  If False, adds no metadata.
            If 'copy', copies metadata from the old root to the new root.

        Returns
        -------
        (Node) the new root node
        """
        from emdfile import Root
        new_root = Root( name=self.root.name+'_cut_'+self.name)
        return self._graft(new_root,merge_metadata=root_metadata)

    def tree(
        self,
        arg = None,
        **kwargs,
        ):
        """
        Usages -

            >>> node.tree()                # show the tree downstream of this node
            >>> node.tree(show=True)       # show the full tree from the root node
            >>> node.tree(show=False)      # show from current node
            >>> node.tree('path/to/node')  # return the node at the chosen location
            >>> node.tree('/path/to/node') # specifiy the location starting from root
            >>> node.tree(node)            # add a child node; must be a Node instance
            >>> node.tree(cut=True)        # remove & return a branch; include root metadata
            >>> node.tree(cut=False)       # discard root metadata
            >>> node.tree(cut='copy')      # copy root metadata
            >>> node.tree(graft=node)      # remove & graft a branch; add new root metadata
            >>> node.tree(graft=(node,False))   # discard root metadata
            >>> node.tree(graft=(node,'copy'))  # copy new root metadata
            >>> node.tree(graft=(node,'overwrite'))  # add root metadata, overwrite conflicts
            >>> node.tree(graft=(node,'copyover'))  # copy root metadata, overwrite conflicts
        """
        # if `arg` is passed, choose behavior from its type
        if isinstance(arg,bool):
            self.show_tree(root=arg)
            return
        elif isinstance(arg,Node):
            if 'force' in kwargs:
                self.force_add_to_tree(arg)
            else:
                self.add_to_tree(arg)
            return
        elif isinstance(arg,str):
            return self.get_from_tree(arg)
        else:
            assert(arg is None), f'invalid `arg` type passed to .tree() {type(arg)}'

        # if `arg` is not passed, choose behavior from **kwargs
        if len(kwargs)==0:
            self.show_tree(root=False)
            return
        else:
            assert(len(kwargs)==1),\
                f"kwargs accepts at most 1 argument; recieved {len(kwargs)}"
            k,v = kwargs.popitem()
            assert(k in ['show','add','get','cut','graft']),\
                f"invalid keyword passed to .tree(), {k}"
            if k == 'show':
                assert(isinstance(v,bool)),\
                    f".tree(show=value) requires type(value)==bool, not {type(v)}"
                self.show_tree(root=v)
            elif k == 'add':
                assert(isinstance(v,Node)),\
                    f".tree(add=value) requires `value` to be a Node, received {type(value)}"
                self.add_to_tree(v)
            elif k == 'get':
                assert(isinstance(v,str)),\
                    f".tree(get=value) requires type(value)==str, not {type(v)}"
                return self.get_from_tree(v)
            elif k == 'cut':
                return self.cut_from_tree(root_metadata=v)
            elif k == 'graft':
                if isinstance(v,Node):
                    n,m = v,True
                else:
                    assert(len(v)==2), ".tree(graft=x) requires `x=Node` or `x=(node,metadata)` for some node and `metadata` in (True,False,'copy')"
                    n,m = v
                return self.graft(node=n,merge_metadata=m)
            else:
                raise Exception(f'Invalid arg {k}; must be in (show,add,get,cut,graft)')

    # decorator for storing params which generated new data nodes
    @staticmethod
    def newnode(method):
        """
        Decorated methods must produce and return a new node.  After decoration
        the new node will be added to the parent node's tree with a Metadata
        instance storing information about how the node was created, namely,
        the method's name, the parent's class and name, and all arguments passed
        to the method.
        """
        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            # Get the called method name
            method_name = method.__name__
            # Get the generating class instance and other args
            self,args = args[0],args[1:]
            # Pair args with names
            method_args = inspect.getfullargspec(method)[0]
            d = dict()
            for i in range(len(args)):
                d[method_args[i]] = args[i]
            # Add the generating class type and name
            d['parent_class'] = self.__class__
            d['parent_name'] = self.name
            d['parent_method'] = method_name
            # Combine with kwargs
            kwargs.update(d)
            # and make the metadata
            md = Metadata( name = "_fn_call_" + method_name )
            md._params.update( kwargs )
            # Run the method, get the returned node
            new_node = method(*args,**kwargs)
            # Add the metadata to the node
            new_node.metadata = md
            # Add the new node to the parent node's tree
            self.tree(new_node)
            # Return
            return new_node
        return wrapper

    ### I/O methods

    @classmethod
    def _get_constructor_args(cls,group):
        """
        Takes an h5py Group corresponding to some EMD node, and returns a
        dictionary of arguments/values to pass to the corresponding class
        constructor.
        """
        # Nodes contain only metadata
        return {
            'name' : basename(group.name)
        }

    def _populate_instance(self,group):
        """
        Run while reading an object from file after initial instantiation.
        Nothing to add for Nodes
        """
        pass

    @classmethod
    def from_h5(cls,group):
        """
        Takes an h5py Group which is open in read mode. Confirms that a
        a Node of this name exists in this group, and loads and returns it
        with it's metadata.

        Parameters
        ----------
        group : h5py Group

        Returns
        -------
        (Node)
        """
        # Validate inputs
        er = f"Group {group} is not a valid EMD node"
        assert("emd_group_type" in group.attrs.keys()), er
        assert(group.attrs["emd_group_type"] in EMD_group_types)

        # Make dict of args to build a new generic class instance
        # then make the new class instance
        args = cls._get_constructor_args(group)
        node = cls(**args)

        # some classes needed to be first instantiated, then populated with data
        node._populate_instance(group)

        # Read any metadata
        try:
            grp_metadata = group['metadatabundle']
            for md in grp_metadata.values():
                node.metadata = Metadata.from_h5(md)
                # check for inherited classes
                if md.attrs['python_class'] != 'Metadata':
                    # and attempt promotion
                    try:
                        cls = _get_class(md)
                        inst = cls( name=basename(md.name) )
                        inst._params.update(node.metadata[basename(md.name)]._params)
                        node.metadata = inst
                    except KeyError:
                        print(f"Warning: unable to promote class from Metadata to {md.attrs['python_class']}")
                        pass
        except KeyError:
            pass

        # Return
        return node

    # write
    def to_h5(self,group):
        """
        Creates a subgroup in `group` and writes this node into that group,
        including the group tags (emd_group_type, python_class), and the
        node's metadata. No data beyond metadata and tags is written.

        Parameters
        ----------
        group : h5py Group

        Returns
        -------
        (h5py Group) the new node's Group
        """
        # Validate group type
        assert(self.__class__._emd_group_type in EMD_group_types)

        # Make group, add tags
        grp = group.create_group(self.name)
        grp.attrs.create("emd_group_type",self.__class__._emd_group_type)
        grp.attrs.create("python_class",self.__class__.__name__)

        # add metadata
        items = self._metadata.items()
        if len(items)>0:
            # create container group for metadata dictionaries
            grp_metadata = grp.create_group('metadatabundle')
            grp_metadata.attrs.create("emd_group_type","metadatabundle")
            for k,v in items:
                # add each Metadata instance
                self._metadata[k].name = k
                self._metadata[k].to_h5(grp_metadata)

        # return
        return grp

class Branch:

    def __init__(self):
        self._dict = {}

    # Enables adding items to the Branch's dictionary
    def __setitem__(self, key, value):
        assert(isinstance(value,Node)), f"only Node instances can be added to tree. not type {type(value)}"
        self._dict[key] = value

    # Enables retrieving items at top level,
    # or nested items using 'node1/node2' syntax
    def __getitem__(self,x):
        l = x.split('/')
        try:
            l.remove('')
            l.remove('')
        except ValueError:
            pass
        return self._getitem_from_list(l)

    def _getitem_from_list(self,x):
        if len(x) == 0:
            raise Exception("invalid slice value to tree")

        k = x.pop(0)
        er = f"{k} not found in tree - check keys"
        assert(k in self._dict.keys()), er

        if len(x) == 0:
            return self._dict[k]
        else:
            tree = self._dict[k]._branch
            return tree._getitem_from_list(x)

    def __delitem__(self,x):
        del(self._dict[x])

    # return the top level keys and items
    def keys(self):
        return self._dict.keys()
    def items(self):
        return self._dict.items()

    # print the full tree contents to screen
    def print(self):
        """
        Prints the tree contents to screen.
        """
        print('/')
        self._print_tree_to_screen(self)
        pass

    @staticmethod
    def _print_tree_to_screen(tree, tablevel=0, linelevels=[]):
        """
        """
        if tablevel not in linelevels:
            linelevels.append(tablevel)
        keys = [k for k in tree.keys()]
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
            try:
                tree._print_tree_to_screen(
                    tree[k]._branch,
                    tablevel=tablevel+1,
                    linelevels=linelevels)
            except AttributeError:
                pass
        pass

    # Displays the top level objects in the Branch
    def __repr__(self):
        space = ' '*len(self.__class__.__name__)+'  '
        string = f"{self.__class__.__name__}( An object tree containing the following top-level object instances:"
        string += "\n"
        for k,v in self._dict.items():
            string += "\n"+space+f"    {k} \t\t ({v.__class__.__name__})"
        string += "\n)"
        return string

