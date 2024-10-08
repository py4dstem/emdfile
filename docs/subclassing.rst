.. defining clases and downstream integration:


Subclassing & Downstream Integration
====================================

``emdfile`` classes are designed to be inherited and used to handle the
read/write interface for other Python projects. To ensure subclasses write and
read correctly, follow the guidelines below.

.. seealso::

    * The :ref:`Node documentation <Node>`
    * The repository `subclassing examples <https://github.com/py4dstem/emdfile/tree/main/samplecode/subclassing_demos>`_
    * Subclassing the :ref:`Custom class <custom-subclassing>`


***********
Module hook
***********

The ``read`` method needs to be able to find your class's definition, and
to do that ``emdfile`` needs to know that your code contains subclasses.
To ensure this, your code should be an importable module with the variable
``_emd_hook = True`` in its top-level namespace.  For instance, this
could be accomplished by placing

.. code-block::

    >>> _emd_hook = True

in the top-level ``__init__.py`` file of a package.


************
Write & Read
************

Each ``emdfile`` Node has a ``.to_h5`` and ``.from_h5`` method which are
used to write to and read from files, respectively. The ``.to_h5`` method
creates an HDF5 group and adds data and metadata.  The ``.from_h5`` method
instantiates a new class instance and populates it with data and metadata
from the HDF5 file.

To create new classes, some modification is needed to ensure read and write
work as expected.  You must modify the

* ``__init__`` and
* ``_get_constructor_args``

methods and circumstantially may need to modify the

* ``_populate_instance`` and
* ``to_h5``

methods. These are each discussed below.


-----
Write
-----

``.to_h5`` will create an HDF5 group and save the metadata and data
normally included with the parent class.  If it needs to be modified,
be sure to call the parent method in the new method definition, e.g.

.. code-block::

    >>> def to_h5(self, group):
    >>>     """ docstring """
    >>>     ...
    >>>     ParentClass.to_h5(group)
    >>>     ...

where ParentClass is the class yours inherits from. You can alternatively
use `super() <https://docs.python.org/3/library/functions.html#super>`_,
as long as you're careful in cases of
`multiple inheritance  <https://www.python.org/download/releases/2.3/mro/>`_.


----
Read
----

In most cases the ``.from_h5`` method should not be modified; instead, methods
it calls should be altered.

``__init__`` must be defined.  It should accept the `name` argument and pass its
value to ParentClass.__init__, which should be called.

``_get_constructor_args`` should be defined, and must return a dictionary of
keyword:value arguments that will be passed to the __init__ method when class
instances are created while reading from disk.

``_populate_instance`` should be defined if a saved class instance may contain
information that is not captured by the ``__init__`` method.  If defined,
this method is run when reading an object from an HDF5 file after instantiation,
enabling additional setup or configuration. For ``Custom`` subclasses, this
method is required.


.. _custom-subclassing:

********************
The ``Custom`` Class
********************

The ``Custom`` class is used for composition of other emdfile class types.

.. seealso::

    * The :ref:`Custom class <Custom>` documentation
    * The repository `subclassing demos <https://github.com/py4dstem/emdfile/tree/main/samplecode/subclassing_demos>`_
    * This `Custom subclassing template <https://github.com/py4dstem/emdfile/blob/main/samplecode/subclassing_demos/custom_subclass_TEMPLATE.py>`_


---------------------------
Inheritance vs. Composition
---------------------------

In inheritance, the child class takes on the properties and methods of the
parent class, and may additionally add new properties and methods of its own.
A new class with a principle data block that is array-, point-, or ragged-array-
like should inherit from Array, PointList, or PointListArray.

Composition is another model for creating a new data-containing class. In
this case, the new class is *composed of* one or more ``emdfile`` classes,
meaning it has one or more attributes pointing to ``emdfile`` class instances,
e.g. an attribute ``.x`` which itself is an ``Array``.  Composition allows
any number of Node-like blocks to be included in a single container.
Inheritance is simpler and should be used any time it is sufficient to meet
requirements. For cases where composition is required, the ``Custom`` class is
provided.

---------------------------------
Defining a ``Custom`` Child Class
---------------------------------

``Custom.to_h5`` will find all class attributes which are ``Node`` instances and
write them to file as subgroups.  However, ``Custom.from_h5`` will not
automatically read these groups - you will therefore need to make sure these
are correctly populated into loaded class instances by modifying the
``__init__``, ``_get_constructor_args``, and ``_populate_instance`` methods.
To do so, the convenience function ``_get_emd_attr_data`` is provided, which
will read all data-node-like subgroups. So using

.. code-block::

    >>> emd_data = cls._get_emd_attr_data(cls,group)

will read all the Node-like data that was stored in class attributes and assign
those objects to the variable ``emd_data``.


