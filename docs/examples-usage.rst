.. usage:

Examples and Usage
==================

Below are introductory examples on

* :ref:`basics <basics>`
* :ref:`trees <build-trees>`
* :ref:`metadata <metadata-example>`
* :ref:`nodes <data-nodes>`
* :ref:`arrays <array-example>`
* :ref:`more data classes <more-data-classes>`
* :ref:`append mode <append-examples>`
* :ref:`defining classes <define-classes>`

See also the
`basic usage <https://github.com/py4dstem/emdfile/blob/main/samplecode/basic_usage.ipynb>`_
notebook in the repo
`sample-code <https://github.com/py4dstem/emdfile/tree/main/samplecode>`_ folder.


.. _basics:

******
Basics
******

.. admonition:: Includes

    * :ref:`Save & read an array <save-read-array>`
    * :ref:`Save & read a dictionary <save-read-dict>`
    * :ref:`Save & read several arrays & dicts <save-read-several>`

After

.. code-block::

    >>> import emdfile as emd, numpy as np

.. _save-read-array:

save and read an array with

.. code-block::

    >>> ar = np.random.random((5,5))
    >>> emd.save(path, ar)
    >>> _ar = emd.read(path)

.. _save-read-dict:

or a Python dictionary with

.. code-block::

    >>> dic = {'a':1, 'b':2}
    >>> emd.save(path, dic)
    >>> _dic = emd.read(path)

.. _save-read-several:

or save a combination of arrays ``ar_*`` and ``dic_*`` with

.. code-block::

    >>> emd.save(path, [ar_A,ar_B,ar_C,dic_X,dic_Y,dic_Z])

and read and unpack them with

.. code-block:: 

    >>> data = emd.read(path)
    >>> _ar_A = data.tree('array_0')
    >>> _ar_B = data.tree('array_1')
    >>> _ar_C = data.tree('array_2')
    >>> _dic_A = data.metadata['dictionary_0']
    >>> _dic_B = data.metadata['dictionary_1']
    >>> _dic_C = data.metadata['dictionary_2']


.. _build-trees:

*****
Trees
*****

.. admonition:: Includes

    * :ref:`Build a tree <build-a-tree>`
    * :ref:`Inspect a Python tree <inspect-python-tree>`
    * :ref:`Save a tree <save-a-tree>`
    * :ref:`Inspect an HDF5 tree <inspect-hdf5-tree>`
    * :ref:`Read from an HDF5 tree <read-hdf5-tree>`

.. _build-a-tree:

``emdfile`` classes can be composed into filetree-like heirarchies. For class
instances ``A``, ``B``, and ``C`` with names ``'A'``, ``'B'`` and ``'C'`` build
a tree with

.. code-block::

    >>> R = emd.Root()
    >>> R.tree(A)
    >>> R.tree(B)
    >>> B.tree(C)

.. _inspect-python-tree:

and display it with 

.. code-block::

    >>> R.tree()

which prints

.. code-block::

    /
    |---A
    |---B
        |---C

.. _save-a-tree:

Save the whole tree with

.. code-block::

    >>> emd.save(path, R)

.. _inspect-hdf5-tree:

then print the file contents with

.. code-block::

    >>> emd.printtree(path)

which prints

.. code-block::

    /
    |---root
        |---A
        |---B
            |---C

.. _read-hdf5-tree:

Read the whole tree again with

.. code-block::

    >>> data = emd.read(path)

or read some subset with

.. code-block::

    >>> data = emd.read(path, emdpath='root/A')             # reads A
    >>> data = emd.read(path, emdpath='root/B')             # reads B---C
    >>> data = emd.read(path, emdpath='root/B', tree=False) # reads B only


.. _metadata-example:

********
Metadata
********

.. admonition:: Includes

    * :ref:`Read dictionaries to Metadata <read-dict-to-metadata>`
    * :ref:`Use Metadata like dictionaries <use-metadata-like-dict>`
    * :ref:`Store various data types <store-data-types>`

.. _read-dict-to-metadata:

When you save a Python dictionary and read it again, you get an ``emd.Metadata``
instance

.. code-block::

    >>> emd.save(path, {'a':1,'b':2})
    >>> x = emd.read(path)
    >>> print(x)
    Metadata( A Metadata instance called 'dictionary', containing the following fields:

          a:   1
          b:   2
    )

.. _use-metadata-like-dict:

You can access values like a normal Python dictionary

.. code-block::

    >>> x['a']
    1

as well as add data

.. code-block::

    >>> x['c'] = 3

.. _store-data-types:

Nested dictionarys of any depth are premitted, as are various Python
and numpy values. Doing

.. code-block::

    >>> m = emd.Metadata( name='my_metadata' )
    >>> m['x'] = True
    >>> m['y'] = np.random.random((3,4,5))
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
    Metadata( A Metadata instance called 'my_metadata', containing the following fields:

          x:   True
          y:   3D-array
          z:   {'alpha': None, 'beta': {'gamma': [10, 11, 12]}}
    )

Any number of Metadata instances can be stored in each emdfile node - see the
:doc:`Metadata <api/classes/metadata>` and :ref:`Node <Node>` docstrings for more
information.


.. _data-nodes:

*****
Nodes
*****

.. admonition:: Includes

    * :ref:`Nodes have names <node-names>`
    * :ref:`Nodes hold arbitrary metadata <nodes-hold-metadata>`
    * :ref:`Nodes have a versatile .tree method <node-tree-method>`

The :ref:`Node <Node>` class is the base class that all
:doc:`emdfile classes <api/classes/index>` inherit from, allowing them
to build and modify trees and store arbitrary metadata. Each node
has a ``.name`` and ``.metadata`` attribute and a ``.tree`` method.

.. _node-names:

A node's name is used to find it in data trees and to save it to
files, and can be assigned during instantiation

.. code-block::

    >>> node = emd.Node( name='my_node' )

.. _nodes-hold-metadata:

The ``.metadata`` property has unique assignment behavior to
allow storing many ``Metadata`` instances in a given node. Doing

.. code-block::

    >>> node.metadata = emd.Metadata('md1',{'x':1,'y':2})
    >>> node.metadata = emd.Metadata('md2',{'a':1,'b':{'c':2,'d':3}})

will store *both* ``Metadata`` instances md1 and md2 in ``node``
(and not overwrite one of them, as you would expect in normal
Python assignment). You can return all the ``Metadata`` instances
in a node with

.. code-block::

    >>> node.metadata
    {'md1': Metadata( A Metadata instance called 'md1', containing the following fields:
     
               x:   1
               y:   2
     ),
     'md2': Metadata( A Metadata instance called 'md2', containing the following fields:
     
               a:   1
               b:   {'c': 2, 'd': 3}
     )}

and one of the ``Metadata`` instances can be retrieved by

.. code-block::

    >>> node.metadata['md1']
    Metadata( A Metadata instance called 'md1', containing the following fields:

              x:   1
              y:   2
    )

.. _node-tree-method:

Basic EMD ``.tree`` usage for building and printing tree structures is
:ref:`shown above <build-trees>`.  Using ``.tree`` you can also retrieve any
tree node, split one tree into two with the ``cut`` operation, or merge two
trees into one with the ``graft`` operation.  EMD trees must begin with a
``Root`` instance, a special ``Node`` subtype intended for this purpose.
See the :ref:`Node <Node>` documentation.



.. _array-example:

******
Arrays
******

.. admonition:: Includes

    * :ref:`Minimal Array instantiation <minimal-array>`
    * :ref:`Arrays with built-in calibrations <array-calibrations>`
    * :ref:`Get or modify dimension vectors <dim-vectors>`

.. _minimal-array:

The :ref:`Array <Array>` class enables storage of array-like data. The
minimal required argument to make a new instance is a numpy array

.. code-block::

    >>> array = emd.Array(np.random.random((3,3)))

.. _array-calibrations:

The ``Array`` class also natively stores some self-descriptive metadata
specifying the data and its coordinate system.  Instantiate an Array instance
with this calibrating metadata included with e.g.

.. code-block::

    >>> ar = emd.Array(
    >>>     np.ones((20,40,1000)),
    >>>     name = '3ddatacube',
    >>>     units = 'intensity',
    >>>     dims = [
    >>>         [0,5],
    >>>         [0,5],
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
first 5 pixels correspond to the locations ``[0,5,10,15,20...]``. Printing
the array to standard output displays the calibration info

.. code-block::

    >>> print(array)
    Array( A 3-dimensional array of shape (20, 40, 1000) called '3ddatacube',
           with dimensions:

               x = [0,5,10,...] nm
               y = [0,5,10,...] nm
               E = [0.0,0.02,0.04,...] eV
    )

.. _dim-vectors:

The dimension vectors, units, and names can all be retrieved or set after
instantiation with various ``Array`` methods like

.. code-block::

    >>> ar.dims
    >>> ar.get_dim
    >>> ar.set_dim
    >>> ar.set_dim_units
    >>> ar.set_dim_name

See the :ref:`Array <Array>` docs for further discussion. ``Array``
instances have all the normal :ref:`Node <data-nodes>` functionality
like ``.metadata`` and ``.tree``.


.. _more-data-classes:

*****************
More Data Classes
*****************

In addition to ``Array``, the normal data-containing classes include ``PointList``
for a set of points in some M dimensional space, and ``PointListArray`` for "ragged
array"-like data, with 2+1 dimensional data currently supported.  For instantiation
and usage, see the :ref:`PointList <PointList>` and
:ref:`PointListArray <PointListArray>` docstrings.

``emdfile`` also includes a ``Custom`` class, designed for composition of the other
class types into a single Node container.  See the
:ref:`defining classes <define-classes>` section below.


.. _append-examples:

***********
Append Mode
***********

.. admonition:: Includes

    * :ref:`Append two EMD trees to one file <append-two-trees-one-file>`
    * :ref:`Append new data into an existing EMD tree <append-existing-tree>`
    * :ref:`Append-over mode to overwrite data <append-over-mode>`

.. _append-two-trees-one-file:

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

.. _append-existing-tree:

If we append to an existing file using a root with a name already in the file,
``emdfile`` will perform a diffmerge-like operation, i.e. it will compare the
two trees, determine which nodes in the incoming tree are new and which
already exist, and write the new nodes to the file. Already existing nodes 
will be skipped if ``mode='a'``, and overwritten if ``mode='ao'``. Note
that comparison happens at the level of node *names*: the contents of the
nodes are not evaluated the the ``save`` function.

For example, if we make a tree and save it

.. code-block::

    >>> root = emd.Root( 'my_root' )
    >>> ar1 = emd.Array(np.ones((5,5)),'array1')
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

.. _append-over-mode:

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
Defining Classes
****************

``emdfile`` is designed for downstream integration, that is, you can build
your own Python scripts, modules, and packages which import ``emdfile`` and
use it to handle reading and writing operations. For more info, see the
:doc:`subclassing guidelines <integration>`.


