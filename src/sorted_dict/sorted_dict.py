"""Custom implementation of a sorted, mutable dict
keeping keys in sorted order and supporting
minimum, maximum, predecessor, and successor operations.

Examples:

>>> # Insert and search
>>> sorted_dict = SortedDict()
>>> sorted_dict[2] = 'two'
>>> sorted_dict[2]
'two'
>>> # Handles duplicate keys
>>> sorted_dict[2] = 'two-two'
>>> sorted_dict[2]
'two-two'
>>> # Multiple keys
>>> sorted_dict[1] = 'one'
>>> sorted_dict.keys()
[1, 2]
>>> # Minimum key
>>> sorted_dict.min()
1
>>> # Non-existing key
>>> sorted_dict[3]
Traceback (most recent call last):
KeyError: ...
### Deleting key
>>> del sorted_dict[1]
>>> sorted_dict[1]
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

    def keys(self):
        return list(self.keys_())

    def keys_(self):
        for key, _ in self.items_():
            yield key

    def items(self):
        return list(self.items_())

    def items_(self):
        for key, value in tree.collect(self._tree):
            yield key, value

    def walk(self, func):
        tree.walk(self._tree, func)

    def min(self):
        return tree.minimum(self._tree)

    def max(self):
        return tree.maximum(self._tree)


__all__ = ["SortedDict"]
