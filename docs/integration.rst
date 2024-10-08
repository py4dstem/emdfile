.. defining clases and downstream integration:


Subclassing & Downstream Integration
====================================

``emdfile`` classes are meant to be extensible, - for example, you could make
make a class of your own which inherits from ``Array``, like

.. code-block::

    class MyDataBlock(Array):
        ...
        def __init__...
        ...

and then store data and metadata, build trees, and save to and read from
files using your new class.  To ensure subclasses write and read correctly
with the ``save`` and ``read`` methods, follow the guidelines below. See
also the :ref:`Node <Node>` documentation, and the repository
`subclassing examples <https://github.com/py4dstem/emdfile/tree/main/samplecode/subclassing_demos>`_.


********************
Subclass module hook
********************

The ``read`` method needs to be able to find your class's definition, and
to do that ``emdfile`` needs to know that your code contains subclasses.
To ensure this, your code must be an importable module with the variable
``_emd_hook = True`` in its top-level namespace.  For instance, this
could be accomplished by placing

.. code-block::

    >>> _emd_hook = True

in the top-level ``__init__.py`` file of a package.


************
Write & Read
************

Each ``emdfile`` Node has a ``.to_h5`` and ``.from_h5`` method which is
used to write to and read from files, respectively. The ``.to_h5`` method
creates an HDF5 group and adds data and metadata.  The ``.from_h5`` method
instantiates a new class instance and populates it with data and metadata.

To create new classes, some modification is needed to ensure read and write
work as expected.  You must modify the

* __init__
* _get_constructor_args

methods and circumstantially may need to modify the

* _populate_instance
* to_h5

methods. These are each discussed below.


-----
Write
-----

``.to_h5`` in general does not need modification. If you need to store data
beyond what is normally included with a node, or to modify data at or just
before write time (e.g. you may want to add class attributes into the
``.metadata``), you can do so by modifying ``.to_h5``.  In this case, the parent
class' ``.to_h5`` method should be run to create the HDF5 group and to save the
normal data and metadata. It accepts the h5py.Group of the parent node. So to
modify ``.to_h5`` you could use

.. code-block::

    >>> def to_h5(self, group):
    >>>     """ docstring """
    >>>     ...
    >>>     ParentClass.to_h5(group)
    >>>     ...

where ParentClass is the class yours inherits from. You can alternatively
use ``super().to_h5`` as long as you're mindfile of the
`inheritance rules <https://www.python.org/download/releases/2.3/mro/>`_
for cases of multiple inheritance.


----
Read
----

In most cases the ``.from_h5`` method should not be modified; instead, methods
it depends on should be altered.

``__init__`` must be defined.  It should accept the `name` argument and pass its
value to ParentClass.__init__, which should be called.

``_get_constructor_args`` should be defined, and must return a dictionary of
keyword:value arguments that will be passed to the __init__ method when class
instances are created while reading from disk.

``_populate_instance`` should be defined if a saved class instance can contain
information that cannot be re-populated by the ``__init__`` method.  If defined,
this method is run when reading this object from an H5 file after instantiation,
enabling additional setup or configuration. For ``Custom`` subclasses, this
method is required.


***************************
Inheritance vs. Composition
***************************

In inheritance, the child class takes on the properties and methods of the
parent class, and may additionally add new properties and methods of its own.
A new class with a principle data block that is array-, point-, or ragged-array-
like should inherit from Array, PointList, or PointListArray.

Composition is nnother model for creating a new data-containing structure. In
this case, the new class is *composed of* one or more ``emdfile`` classes,
meaning it has attributes pointing to ``emdfile`` class instances, e.g. a class
with a ``.my_array`` attribute which itself is an ``Array``.  Composition allows
any number of Node-like blocks to be included in a single container.
Inheritance should be used any time it is sufficient to meet requirements. For
cases where composition is required, the ``Custom`` class is provided.

--------------------
The ``Custom`` Class
--------------------

``Custom.to_h5`` will find all class attributes which are ``Node`` instances and
write them to file as subgroups.  However, ``Custom.from_h5`` will not
automatically read these groups - you will therefore need to make sure these
are correctly populated into loaded class instances by modifying the
``__init__``, ``_get_constructor_args``, and ``_populate_instance`` methods.
To do so, the convenience function ``_get_emd_attr_data`` is provided, which
will read all data-node-like subgroups. So using

.. code-block::

    >>> emd_data = cls._get_emd_attr_data(cls,group)

will read all the data that was stored in class attributes and assign those
objects to the variable ``emd_data``.

For more information see the :ref:`Custom class <Custom>` docs, the repository
`subclassing demos <https://github.com/py4dstem/emdfile/tree/main/samplecode/subclassing_demos>`_,
and the
`Custom subclassing template <https://github.com/py4dstem/emdfile/blob/main/samplecode/subclassing_demos/custom_subclass_TEMPLATE.py>`_.

