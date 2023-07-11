from typing import Optional
from os.path import basename
import h5py

from emdfile.classes import Metadata
from emdfile.classes.utils import EMD_group_types, _get_class


class Node:
    """
    Nodes contain attributes and methods paralleling
    the EMD 1.0 file specification in Python runtime objects.

    EMD 1.0 is a singly-rooted file format.  That is to say:
    An EMD data object can and must exist in one and only one
    EMD tree. An EMD file can contain any number of EMD trees, each
    containing data and metadata which is, within the limits of
    the EMD group specifications, of some arbitrary complexity.
    An EMD 1.0 file thus represents, stores, and enables
    access to some arbitrary data in long term storage on a file
    system in the form of an HDF5 file.  The Node class provides
    machinery for building trees of data and metadata which mirror
    the EMD tree format but which exist in a live Python instance,
    rather than on the file system. This facilitates ease of
    transfer between Python and the file system.

    Nodes are intended to be used a base class on which other, more
    complex classes can be biult. Nodes themselves contain the
    machinery for managing a tree heirarchy of other Nodes and
    Metadata instances, and for reading and writing those trees.
    They do not contain any particular data. Classes storing data
    and analysis methods which inherit from Node will inherit its
    tree management and EMD i/o functionality.

    Below, the 4 elements of the node class are each described in turn:
    roots, trees, metadata, and i/o.


    ROOTS

    EMD data objects can and must exist in one and only one EMD tree,
    each of which must have a single, named root node. To parallel this in
    our runtime objects, each Node has a root property, which can be found
    by calling `self.root`.

    By default new nodes have their root set to None. If a node
    with `.root == None` is saved to file, it is placed inside a
    new root with the same name as the object itself, and this
    is then saved to the file as a new (minimal) EMD tree.

    A new root node can be instantiated by calling

        >>> rootnode = Root(name=some_name).

    Objects added to an existing rooted tree (including a new root node)
    automatically have their root assigned to the root of that tree.
    Adding objects to trees is discussed below.


    TREES

    The tree associated with a node can be manipulated with the .tree
    method. If we have some rooted node `node1` and some unrooted node
    `node2`, the unrooted node can be added to the existing tree as a
    child of the rooted node with

        >>> node1.tree(node2)

    If we have a rooted node `node1` and another rooted node `node2`,
    we can't simply add node2 with the code above, as this would
    create a conflict between the two roots.  In this case, we can
    move node2 from its current tree to the new tree using

        >>> node1.tree(graft=node2)

    The .tree method has various additional functionalities, including
    printing the tree, retrieving objects from the tree, and cutting
    branches from the tree.  These are summarized below:

        >>> .tree()             # show tree from current node
        >>> .tree(show=True)    # show from root
        >>> .tree(show=False)   # show from current node
        >>> .tree(add=node)     # add a child node
        >>> .tree(get='path')   # return a '/' delimited child node
        >>> .tree(get='/path')  # as above, starting at root
        >>> .tree(cut=True)     # remove/return a branch, keep root metadata
        >>> .tree(cut=False)    # remove/return a branch, discard root md
        >>> .tree(cut='copy')   # remove/return a branch, copy root metadata
        >>> .tree(graft=node)   # remove/graft a branch, keep root metadata
        >>> .tree(graft=(node,True))    # as above
        >>> .tree(graft=(node,False))   # as above, discard root metadata
        >>> .tree(graft=(node,'copy'))  # as above, copy root metadata

    The show, add, and get methods can be accessed directly with

        >>> .tree(arg)

    for an arg of the appropriate type (bool, Node, and string), i.e.
    in most cases, the keyword can be dropped.  So

        >>> .tree()
        >>> .tree(node)
        >>> .tree(True)
        >>> .tree('some/node')

    will, respectively, print the tree from the current node to screen,
    add the node `node` to the tree, pring the tree from the root node
    to screen, and return the node at the emdpath 'some/node'.

    If a node needs to be added to a tree and it may or may not
    already have its own root, calling

        >>> .tree(add=node, force=True)

    or

        >>> .tree(node, force=True)

    will add the node to the tree, using a simple add if node has no
    root, and grafting it if it does have a root.


    METADATA

    Nodes can contain any number of Metadata instances, each of which
    wraps a Python dictionary of some arbitrary complexity (to within
    the limits of the Metadata group EMD specification, which limits
    permissible values somewhat).

    The code:

        >>> md1 = Metadata(name='md1')
        >>> md2 = Metadata(name='md2')
        >>> <<<  some code populating md1 + md2 >>>
        >>> node.metadata = md1
        >>> node.metadata = md2

    will create two Metadata objects, populate them with data, then
    add them to the node.  Note that Node.metadata is *not* a Python
    attribute, it is specially defined property, such that the last
    line of code does not overwrite the line before it - rather,
    assigning to the .metadata property adds the new metadata object
    to a running dictionary of arbitrarily many metadata objects.
    Both of these two metadata instances can therefore still be
    retrieved, using:

        >>> x = node.metadata['md1']
        >>> y = node.metadata['md2']

    Note, however, that if the second metadata instance has an identical
    name to the first instance, then in *will* overwrite the old instance.


    I/O

    # TODO

    """
    _emd_group_type = 'node'

    def __init__(
        self,
        name: Optional[str] = 'node'
        ):
        self.name = name
        self._branch = Branch()     # enables accessing child groups
        self._treepath = None   # enables accessing parent groups
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



    ########## .tree methods ###########

    def show_tree(self,root=False):
        """
        Display the object tree. If `root` is False, displays the branch
        of the tree downstream from this node.  If `root` is True, displays
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
        Add an unrooted node as a child of the current, rooted node.
        To move an already rooted node/branch, use `.graft()`.
        To create a rooted node, use `Root()`.
        """
        assert(isinstance(node,Node))
        assert(self.root is not None), "Can't add objects to an unrooted node. See the Node docstring for more info."
        assert(node.root is None), "Can't add a rooted node to a different tree.  Use `.tree(graft=node)` instead."
        node._root = self._root
        self._branch[node.name] = node
        node._treepath = self._treepath+'/'+node.name

    def force_add_to_tree(self,node):
        """
        Add node `node` as a child of the current node, whether or not
        `node` is rooted.  If it's unrooted, performs a simple add. If
        it is rooted, performs a graft, excluding the root metadata
        from `node`.
        """
        try:
            self.add_to_tree(node)
        except AssertionError:
            self.graft(node, merge_metadata=False)


    def get_from_tree(self,name):
        """
        Finds and returns an object from an EMD tree using the string
        key `name`, with '/' delimiters between 'parent/child' nodes.
        Search from the root node by adding a leading '/'; otherwise,
        searches from the current node.
        """
        if name == '':
            return self.root
        elif name[0] != '/':
            return self._branch[name]
        else:
            return self.root._branch[name]

    def _graft(self,node,merge_metadata=True):
        """
        Moves the branch beginning at this node onto another tree at
        targed point `node`.

        This is the reverse of the behavior of self.graft(node), which moves
        the branch on some other tree beginning at `node` onto this tree
        starting at this node. In other words, self.graft() grafts onto self,
        while self._graft() grafts from self.

        Accepts:
            node (Node):
            merge_metadata (True, False, 'copy', or 'overwrite'): if True adds
                the new root's metadata to the old root, skipping entries that
                exist in both; overwrite is identical, but overwrites entries
                that exist in both; if False adds no metadata to the new
                root; if 'copy' adds copies of all metadata from the old root to
                the new root.

        Returns:
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
        assert(merge_metadata in [True,False,'copy','overwrite'])
        if merge_metadata is False:
            # add no root metadata
            pass
        elif merge_metadata is True:
            # add old root metadata to new root
            for key in old_root.metadata.keys():
                if key not in node.root.metadata.keys():
                    node.root.metadata = old_root.metadata[key]
        elif merge_metadata == "overwrite":
            # add old root metadata to new root
            for key in old_root.metadata.keys():
                node.root.metadata = old_root.metadata[key]
        else:
            # add copies of old root metadata to new root
            for key in old_root.metadata.keys():
                node.root.metadata = old_root.metadata[key].copy()
        # return
        return node.root


    def graft(self,node,merge_metadata=True):
        """
        Moves the branch beginning node onto this tree at this node.

        For the reverse (i.e. grafting from this tree onto another tree)
        either use that tree's .graft method, or use this tree's ._graft.

        Accepts:
            node (Node):
            merge_metadata (True, False, or 'copy'): if True adds the old root's
                metadata to the new root; if False adds no metadata to the new
                root; if 'copy' adds copies of all metadata from the old root to
                the new root.

        Returns:
            (Node) this tree's root node
        """
        return node._graft(
            self,
            merge_metadata=merge_metadata
        )


    def cut_from_tree(self,root_metadata=True):
        """
        Removes a branch from an object tree at this node.

        A new root node is created under this object
        with this object's name.  Metadata from
        the current root is transferred/not transferred
        to the new root according to the value of `root_metadata`.

        Accepts:
            root_metadata (True, False, or 'copy'): if True adds the old root's
                metadata to the new root; if False adds no metadata to the new
                root; if 'copy' adds copies of all metadata from the old root to
                the new root.

        Returns:
            (Node) the new root node
        """
        new_root = Root( name=self.root.name+'_cut_'+self.name)
        return self._graft(new_root,merge_metadata=root_metadata)


    def tree(
        self,
        arg = None,
        **kwargs,
        ):
        """
        Usages -

            >>> .tree()             # show tree from current node
            >>> .tree(show=True)    # show from root
            >>> .tree(show=False)   # show from current node
            >>> .tree(add=node)     # add a child node
            >>> .tree(get='path')   # return a '/' delimited child node
            >>> .tree(get='/path')  # as above, starting at root
            >>> .tree(cut=True)     # remove/return a branch, keep root metadata
            >>> .tree(cut=False)    # remove/return a branch, discard root md
            >>> .tree(cut='copy')   # remove/return a branch, copy root metadata
            >>> .tree(graft=node)   # remove/graft a branch, keeping root metadata
            >>> .tree(graft=(node,True))    # as above
            >>> .tree(graft=(node,False))   # as above, discard root metadata
            >>> .tree(graft=(node,'copy'))  # as above, copy root metadata

        The show, add, and get methods can be accessed directly with

            >>> .tree(arg)

        for an arg of the appropriate type (bool, Node, and string).
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

    ########## end .tree methods ###########



    # decorator for storing params which generated new data nodes

    @staticmethod
    def newnode(method):
        """
        Decorator which may be added to node methods which product and
        return a new node.  If such a method is decorated with

        >>> @newnode

        then the new node is added to the parent node's tree, and a
        Metadata instance is added to the new node's metadata which
        stores information about how the node was created, namely:
        method's name, the parent's class and name, and all
        the arguments passed to method.
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




    # read

    # this machinery is designed to work with and be extendible
    # in the context of child classes.

    # to add a new child class, only a new _get_constructor_args()
    # classmethod should be necessary. If a class needs additional
    # construction post-initialization, define a _populate_instance()
    # method. The .from_h5 function should not need any modification.

    @classmethod
    def _get_constructor_args(cls,group):
        """
        Takes a group, and returns a dictionary of args/values
        to pass to the class constructor
        """
        # Nodes contain only metadata
        return {
            'name' : basename(group.name)
        }


    def _populate_instance(self,group):
        """ Nothing to add for Nodes
        """
        pass



    @classmethod
    def from_h5(cls,group):
        """
        Takes an h5py Group which is open in read mode. Confirms that a
        a Node of this name exists in this group, and loads and returns it
        with it's metadata.

        Accepts:
            group (h5py Group)

        Returns:
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
        Takes an h5py Group instance and creates a subgroup containing
        this node, tags indicating the groups EMD type and Python class,
        and any metadata in this node.

        Accepts:
            group (h5py Group)

        Returns:
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









class Root(Node):
    """
    A Node instance with its .root property set to itself.
    """
    _emd_group_type = 'root'

    def __init__(self,name='root'):
        Node.__init__(self,name=name)
        self._treepath = ''
        self._root = self










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




