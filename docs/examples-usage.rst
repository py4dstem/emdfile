.. usage:

Examples and Usage
==================

After

.. code-block::

    >>> import emdfile as emd, numpy as np

save and read an array with

.. code-block::

    >>> ar = np.random.rand((5,5))
    >>> emd.save(path, ar)
    >>> _ar = emd.read(path)

or a Python dictionary with

.. code-block::

    >>> dic = {'a':1, 'b':2}
    >>> emd.save(path, dic)
    >>> _dic = emd.read(path)

or save a combination of arrays ``ar_*`` and ``dic_*`` with

.. code-block::

    >>> emd.save(path, [ar_A,ar_B,ar_C,dic_X,dic_Y,dic_Z])

and read and unpack them with

.. code-block:: 

    >>> data = emd.read(path)
    >>> _ar_A = data.tree('ar0')
    >>> _ar_B = data.tree('ar1')
    >>> _ar_C = data.tree('ar2')


.. _build-trees:

***********
Build Trees
***********

The ``emdfile`` classes can hold datasets, calibrations, and arbitrary metadata
- see e.g. the :ref:`Array <Array>` docs or :ref:`this example <array-example>`.
They can also be composed into filetree-like heirarchies.  For ``emdfile`` class
instances ``A``, ``B``, and ``C`` with names ``'A'``, ``'B'`` and ``'C'`` build
a tree with

.. code-block::

    >>> R = emd.Root()
    >>> R.tree(A)
    >>> R.tree(B)
    >>> B.tree(C)

and display it with 

.. code-block::

    >>> R.show()

which prints

.. code-block::

    root
      |---A
      |---B
          |---C

Save, then print the file contents with

.. code-block::

    >>> emd.save(path, R)
    >>> emd.printtree(path)

which prints

.. code-block::

    root
      |---A
      |---B
          |---C

Read the whole tree again with

.. code-block::

    >>> data = emd.read(path)

or read some subset with

.. code-block::

    >>> data = emd.read(path, emdpath='A')                  # reads A
    >>> data = emd.read(path, emdpath='B')                  # reads B---C
    >>> data = emd.read(path, emdpath='B', tree=False)      # reads B only


.. _metadata-example:

****************
Include Metadata
****************

When you save a Python dictionary and read it again, you get an ``emd.Metadata``
instance

.. code-block::

    >>> emd.save(path, {'a':1,'b':2})
    >>> x = emd.read(path)
    >>> print(x)
    TODO

You can access values like a normal Python dictionary

.. code-block::

    >>> x['a']
    1

as well as add data

.. code-block::

    >>> x['c'] = 3

Nested dictionarys of any depth are premitted, as are various Python
and numpy values. Doing

.. code-block::

    >>> m = emd.Metadata( name='my_metadata' )
    >>> m['x'] = True
    >>> m['y'] = np.random.rand((3,4,5))
    >>> m['z'] = {
    >>>     'alpha' : None,
    >>>     'beta' : {
    >>>         'gamma' : [10,11,12]
    >>>     }
    >>> }
    >>> emd.save(path, m)

saves a dictionary and

.. code-block::

    >>> _m = emd.read(path)

reads it again. Print its contents with

.. code-block::

    >> print(_m)
    TODO

Any number of Metadata instances can be stored in each emdfile node - see the
:doc:`Metadata <api/classes/metadata>` and :ref:`Node <Node>` docstrings for more
information.


.. _data-nodes:

******************
Working with Nodes
******************

The :ref:`Node <Node>` class is the base class that all
:doc:`emdfile classes <api/classes/index>` inherit from, allowing them
to build and modify trees and store arbitrary metadata. Each node
has a ``.name`` and ``.metadata`` attribute and a ``.tree`` method.

A node's name is used to find it in data trees and to save it to
files, and can be assigned during instantiation

.. code-block::

    >>> node = emd.Node( name='my_node' )

The ``.metadata`` property has unique assignment behavior to
allow storing many ``Metadata`` instances in a given node. Doing

.. code-block::

    >>> node.metadata = Metadata('md1',{'x':1,'y':2})
    >>> node.metadata = Metadata('md2',{'a':1,'b':{'c':2,'d':3}})

will store *both* ``Metadata`` instances md1 and md2 in ``node``
(and not overwrite one of them, as you would expect in normal
Python assignment). You can return all the ``Metadata`` instances
in a node with

.. code-block::

    >>> node.metadata

which, in this example, will return

.. code-block::

    {...TODO...}

and one of the ``Metadata`` instances can be retrieved by

.. code-block::

    >>> node.metadata['md1']

Basic EMD ``.tree`` usage for building and printing tree structures is
:ref:`shown above <build-trees>`.  Using ``.tree`` you can also retrieve any
tree node, split one tree into two with the ``cut`` operation, or merge two
trees into one with the ``graft`` operation.  EMD trees must begin with a
``Root`` instance, a special ``Node`` subtype intended for this purpose.
See the :ref:`Node <Node>` documentation.



.. _array-example:

********************************
Arrays and Built-in Calibrations
********************************

The :ref:`Array <Array>` class enables storage of array-like data of
any dimensionality

.. code-block::

    >>> array = emd.Array(np.random.rand((3,3)))

and also natively stores specific metadata intended to describe the
data and its coordinate system.  Instantiate an Array instance with
this calibrating metadata included with, e.g.

.. code-block::

    >>> ar = Array(
    >>>     np.ones((20,40,1000)),
    >>>     name = '3ddatacube',
    >>>     units = 'intensity',
    >>>     dims = [
    >>>         [0,5],
    >>>         [0,5]
    >>>         [0,0.02],
    >>>     ],
    >>>     dim_units = [
    >>>         'nm',
    >>>         'nm',
    >>>         'eV'
    >>>     ],
    >>>     dim_names = [
    >>>         'x',
    >>>         'y',
    >>>         'E',
    >>>     ],
    >>> )

where ``dims`` generates vectors which calibrate each of the array's axes.
In the case above, the two numbers given (e.g. ``[0,5]`` for each of the
first two dimensions) are linearly extrapolated, so the first dimension's
first 5 pixels correspond to the locations ``[0,5,10,15,20...]``. The
dimension vectors, units, and names can all be retrieved or set after
instantiation with various ``Array`` methods like

.. code-block::

    >>> ar.dims
    >>> ar.get_dim(n)
    >>> ar.set_dim
    >>> ar.set_dim_units
    >>> ar.set_dim_name

See the :ref:`Array <Array>` docs for further discussion. ``Array``
instances have all the normal :ref:`Node <data-nodes>` functionality
like ``.metadata`` and ``.tree``.  See also the :ref:`PointList <PointList>`
and :ref:`PointListArray <PointListArray>` datatypes.



.. _append-examples:

*************************************
Appending and Complex Write Behaviors
*************************************

In addition to writing new files, ``emdfile`` allows appending new data to
existing files. If we first write some tree

.. code-block::

    >>> root1 = emd.Root('root1')
    >>> root1.tree( <add some data> )
    >>> emd.save(path, root1)

and then later make a second tree of data

.. code-block::

    >>> root2 = emd.Root('root2')
    >>> root2.tree( <add some other data> )

the second tree can be added to the same file using "append" mode

.. code-block::

    >>> emd.save(path, root2, mode='a')

The two trees will both be saved to the same file, each starting
at their own root group just under the HDF5 root, provided that the
``Root`` instances have different names.

If we append to an existing file using a root with a name already in the file,
``emdfile`` will perform a diffmerge-like operation, i.e. it will compare the
two trees, determine which nodes in the incoming tree are new and which
already exist, and write the new nodes to the file. Already existing nodes 
will be skipped if ``mode='a'``, and overwritten if ``mode='ao'``. Note
that comparison happens at the level of node *names*: the contents of the
nodes are not evaluated the the ``save`` function.

For example, if we make a tree and save it

.. code-block::

    >>> root = emd.root( 'my_root' )
    >>> ar1 = emd.Array(np.ones((5,5),'array1'))
    >>> root.tree(ar1)
    >>> emd.save(path, root)

then add more data later

.. code-block::

    >>> ar2 = emd.Array(np.zeros((3,3,3)),'array2')
    >>> ar1.tree(ar2)

then we can grow the tree saved to the filesystem at ``path`` with

.. code-block::

    >>> emd.save(path, root, mode='a')

After the first write operation, the file tree will look like

.. code-block::

    my_root
      |---ar1

and after the second operation it will be

.. code-block::

    my_root
      |---ar1
            |---ar2

What if the data in ``ar1`` is changed some time after its been
written to file?  E.g. 

.. code-block::

    >>> ar1.data += np.random.rand((5,5))

In this case, this change will *not* be reflected in the file if we
perform a normal append operation like

.. code-block::

    >>> emd.save(path, root, mode='a')

but *will* be reflected in the file if we perform an "append-over" operation,
e.g.

.. code-block::

    >>> emd.save(path, root, mode='ao')

Note, however, that this append-over will overwrite every node appearing in
both the runtime and filesystem trees (in this case, just ``'ar1'`` and
``'ar2'``).  Moreover, the system storage that's been overwritten is not
freed by this operation, so overwriting large data blocks is not recommended,
unless followed up by re-packing the files, e.g. by subsequently copying then
deleting the original file.

More targetted save operations - e.g. adding or overwriting a single node, or
appending a specific tree branch downstream of a selected node - are also
possible. See the :ref:`save <save>` docs for more info.




.. _define-classes:

****************
Defining classes
****************

``emdfile`` is designed for downstream integration, that is, you can build
your own Python scripts, modules, and packages which import ``emdfile`` and
use it to handle reading and writing operations. In particular, its classes
are meant to be extensible - for example, you could make a class of your own
which inherits from ``Array``, like

.. code-block::

    class MyDataBlock(Array):
        ...
        def __init__...
        ...

and then store data and metadata, build trees, and save to and read from
files using your new class.  For more info on class inheritance and
downstream package integration, see the docs for the :ref:`Node <Node>` and
:ref:`Custom <Custom>` classes.







