.. module utilities

Utilities
=========

Find below the ``emdfile`` :ref:`module-level <module-utilities>` and :ref:`class-level <class-utilities>` utilities.
Note that ``emdfile`` also contains an :ref:`N-dimensional progress bar <tqdmnd>` utility, curtesy of `Steven E. Zeltmann <https://github.com/sezelt>`_.


.. _module-utilities:

**********************
Module Level Utilities
**********************

.. autofunction:: emdfile.utils._is_EMD_file
.. autofunction:: emdfile.utils._get_EMD_version
.. autofunction:: emdfile.utils._version_is_geq
.. autofunction:: emdfile.utils._get_UUID
.. autofunction:: emdfile.utils._read_metadata
.. autofunction:: emdfile.utils._get_EMD_rootgroups



.. _class-utilities:

*********************
Class Level Utilities
*********************

.. autofunction:: emdfile.classes.utils._get_class
.. autofunction:: emdfile.classes.utils._get_dependent_packages
.. autofunction:: emdfile.classes.utils._walk_module_find_classes



.. _tqdmnd:

**************************
N-dimensional Progress Bar
**************************

``tqdmnd`` is an extension of the classic ``tqdm`` progress-bar module to support for-loops nested to any level.  See also `here <https://gist.github.com/sezelt/61274e6f96db5190204f295dcbe6cc2c>`_ for Steve's standalone version.

.. autofunction:: emdfile.tqdmnd


