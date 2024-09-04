import sys
import types
import inspect

# Define the EMD group types
EMD_base_group_types = (
    "root",
    "metadatabundle",
    "metadata",
)
EMD_data_group_types = (
    "node",
    "array",
    "pointlist",
    "pointlistarray",
    "custom",
)
EMD_custom_group_types = tuple(
    ["custom_"+s for s in EMD_data_group_types]
)
EMD_group_types = EMD_base_group_types + EMD_data_group_types + EMD_custom_group_types

def _get_class(grp):
    """
    Returns a dictionary of Class constructors from corresponding strings
    """
    from emdfile import classes
    # Build lookup table for classes
    lookup = {}
    for name, obj in inspect.getmembers(classes):
        if inspect.isclass(obj):
            lookup[name] = obj
    # hook for dependent package classes
    for module in _get_dependent_packages():
        _walk_module_find_classes(module, lookup)
    # Get the class from the group tags and return
    try:
        classname = grp.attrs['python_class']
        __class__ = lookup[classname]
        return __class__
    except KeyError:
        raise Exception(f"Unknown classname {classname}")

def _get_dependent_packages():
    """
    Searches packages with the top level attribute "_emd_hook" = True.
    Returns a generator of all such packages
    """
    mods = sys.modules.values()
    for module in mods:
        if isinstance(module, types.ModuleType):
            if hasattr(module, "_emd_hook"):
                if module._emd_hook is True:
                    yield module

def _walk_module_find_classes(mod, dic, depth=0, maxdepth=6):
    """
    Searches the tree of a Python module for emd classes, and
    populates dictionary dic with them
    """
    from emdfile import Node,Metadata
    if depth >= maxdepth:
        return
    for name, obj in inspect.getmembers(mod):
        if inspect.isclass(obj):
            if Node in obj.mro() or Metadata in obj.mro():
                dic[name] = obj
            else:
                pass
        elif inspect.ismodule(obj):
            if hasattr(obj, "_emd_hook"):
                if obj._emd_hook == True:
                    _walk_module_find_classes(
                        obj, dic, depth=depth+1, maxdepth=maxdepth)
        else:
            pass
