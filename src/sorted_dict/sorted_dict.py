"""Custom implementation of a sorted, mutable dict
keeping keys in sorted order and supporting
minimum, maximum, predecessor, and successor operations.

Examples:

>>> tree = SortedDict()
>>> tree[1] = 'one'
>>> tree[1]
'one'
>>> tree[2]
Traceback (most recent call last):
KeyError: ...
>>> del tree[1]
>>> tree[1]
Traceback (most recent call last):
KeyError: ...
"""
from . import tree


class SortedDict:
    def __init__(self):
        self._tree = tree.Tree()

    def __setitem__(self, key, item):
        tree.insert(self._tree, key, item)

    def __getitem__(self, key):
        return tree.search(self._tree, key)

    def __delitem__(self, key):
        return tree.delete(self._tree, key)

    def __contains__(self, key):
        try:
            self[key]
            return True
        except KeyError:
            return False

    def inorder_walk(self, func):
        tree.walk(self._tree, func)


__all__ = ["SortedDict"]
