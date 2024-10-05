.. trees

Trees
=====

All ``emdfile`` data classes inherit from the :ref:`Node <Node>` class, which adds core tree-building and metadata storage functionality.
EMD trees must begin at an instance of the :ref:`Root <Root>` class.
To define new classes which make use of the emdfile :ref:`read <read>` and :ref:`save <save>` methods, see the :ref:`Node <Node>` docstring.
The :ref:`Custom <Custom>` class enables composition of emdfile classes.



.. _Node:

****
Node
****

.. autoclass:: emdfile.classes::Node
    :members:

.. _Root:

****
Root
****

.. autoclass:: emdfile.classes::Root
    :members:

.. _Custom:

******
Custom
******

.. autoclass:: emdfile.classes::Custom
    :members:

