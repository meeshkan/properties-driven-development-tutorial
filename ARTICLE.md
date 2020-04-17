---
title: Properties-driven development in Python
---

### Why this article?

- Goal: Educate developers about properties-driven development
- Audience: Developers writing tests

### Introduction

Tests guide development:

- Testing is not about finding bugs, they are the first user of your code
- Your imagination is limited: you can't figure out all the ways things can go wrong
- You may also encode your unconscious assumptions into tests -> You should explicitly state those assumptions

Enter property-based testing:

- Properties are great for verifying assumptions. Let computer generate the data for your properties.
- Test contracts and invariants instead of hard-coded inputs and outputs
- Forces you to **think** about contracts and invariants

Enter properties-driven development:

1. Imagine how your code would be used (possibly adding as doctest)
2. Generalize your examples into properties
3. Pick a property from the list
4. Code the properties, ensuring generators work as expected (possibly even writing tests for your generators)
5. Implement actual code. Don't be afraid to tweak the property.
6. If everything looks good and there are properties left, go to 3. If your examples or properties need re-thinking, go to 1.

### Example

- Implement our own dictionary keeping keys in sorted order
- Keys and values kept in a binary search tree
- Insertions, searches, deletions O(lg n) on average
- Unbalanced, you should use [`sortedcontainers`](https://github.com/grantjenks/python-sortedcontainers/) for anything real

Why this?

1. Property-based tests are not only for functional programming
1. It's complex enough to possibly have tricky bugs
1. I'm interested in datastructures and algorithms

### What the code should do

```python
>>> # Insert and search
>>> sorted_dict = SortedDict()
>>> sorted_dict[2] = 'two'
>>> sorted_dict[2]
'two'
>>> # Handles duplicate keys
>>> sorted_dict[2] = 'two-two'
>>> 'two-two'
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
```

This serves as `doctest`!

### Write down properties

1. Key-value pairs added to sorted dictionary can be searched.
1. Adding key that exists overwrites the existing one.
1. Keys are sorted.
1. Searching for minimum key returns the smallest key.
1. Searching for non-existing key raises `KeyError`.
1. Deleting a key and then searching it raises `KeyError`

### Write our first property

#### Define `SortedDict`

```python
class SortedDict:
    def __init__(self):
        self._tree = tree.Tree()

    def __setitem__(self, key, item):
        pass

    def __getitem__(self, key):
        pass
```

#### Define binary search tree

```python
import typing as t

@dataclass
class Tree:
    """Binary search tree.
    """

    root: t.Optional[Node] = None

    def __repr__(self):
        return "Tree with root: {}".format(repr(self.root))
```

```python
@dataclass
class Node:
    key: int
    value: t.Any
    parent: t.Optional["Node"] = None
    left: t.Optional["Node"] = None
    right: t.Optional["Node"] = None

    def __repr__(self):
        return "Key: {}, Left: ({}), Right: ({})".format(
            self.key, repr(self.left), repr(self.right)
        )
```

#### Define data generators

```python
def some_key_value_tuples():
    """Generator for lists of key-value tuples.
    """
    some_keys = some.integers()
    some_values = some.binary()
    some_kvs = some.tuples(some_keys, some_values)
    return some.lists(some_kvs)
```

```python
@some.composite
def some_sorted_dicts(draw):
    """Generator of sorted dicts along with the dictionary of
    key-value pairs used for constructing it."""
    key_values = draw(some_key_value_tuples())

    sorted_dict = SortedDict()
    for key, val in key_values:
        sorted_dict[key] = val

    # Put the keys you expect to find in sorted_dict
    # in a dictionary for comparison.
    expected = {}
    for key, val in key_values:
        expected[key] = val

    return sorted_dict, expected
```

#### Define the property

```python
@given(dict_and_values=some_sorted_dicts())
def test_insert_and_search(dict_and_values):
    """Key-value pairs added to sorted dictionary can be searched."""
    sorted_dict, expected = dict_and_values

    for key, value in expected.items():
        in_dict = sorted_dict[key]
        assert in_dict == value, "Expected {} for key {}, got {}".format(
            value, key, in_dict
        )
```

#### Define insert and search

### Verify invariant: keys are sorted

### Verify deletion works

### Conclusion

- Positive vs. negative testing
