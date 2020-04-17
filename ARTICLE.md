---
title: Introduction to properties-driven development
description: We'll teach you what property-driven development is is and how to apply it for a project.
slug: introduction-to-properties-driven-development
date: 2020-04-17
authors: ["kimmo"]
tags:
  - testing
  - tutorial
  - beginners
  - python
---

> _This article was edited by [Carolyn Stransky](https://dev.to/carolstran). XXX and XXX are acknowledged for their feedback._

Tests guide development:

- Testing is not about finding bugs, they are the first user of your code
- Your imagination is limited: you can't figure out all the ways things can go wrong
- You may also encode your unconscious assumptions into tests -> You should explicitly state those assumptions

Enter property-based testing:

- Properties are great for verifying assumptions. Let computer generate the data for your properties.
- Test contracts and invariants instead of hard-coded inputs and outputs
- Forces you to **think** about contracts and invariants, explicitly stating the limits of your code

Enter properties-driven development:

1. Imagine how your code would be used
2. Generalize your examples into properties
3. Pick a property from the list
4. Code the properties, ensuring generators work as expected (possibly even writing tests for your generators)
5. Implement actual code. Don't be afraid to tweak the property.
6. If everything looks good and there are properties left, go to 3. If your examples or properties need re-thinking, go to 1.

Enter this article:

- How to apply the principles to implement a datastructure

## ToC

- Example project: sorted dictionary

  - What should it do?
  - Coming up with properties

- Coding the first property

  - Coding the generator
  - Coding the property

- Making the property pass

  - Binary search tree
  - Sorted dictionary

- Coding invariant

- Handling deletion

- Final touch: add `doctest`

- Bonus: stateful testing

- [Conclusion](#conclusion)
- [Resources](#resources)

⚠️ **Prerequisites**:

- A general understanding of software testing
- (Optional) [Python 3+](https://www.python.org/downloads/)\* if you want to follow along

_\* This guide will use Python for code examples, but the concepts aren't limited to any specific programming language. So even if you don't know Python, we'd encourage you to read along anyway._

💻 **References**:
This [GitHub repository](https://github.com/meeshkan/properties-driven-development-tutorial) contains all the featured code examples as tests. The repository also contains instructions for how to execute them.

## Example project: sorted dictionary

- Implement our own dictionary keeping keys in sorted order
- Keys and values kept in a binary search tree
- Insertions, searches, deletions O(lg n) on average
- Unbalanced, you should use [`sortedcontainers`](https://github.com/grantjenks/python-sortedcontainers/) for anything real

Why this?

1. Property-based tests are not only for functional programming
1. It's complex enough to possibly have tricky bugs
1. It's simple enough to contain well-known reference implementation

### What should it do?

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

### Coming up with properties

1. Key-value pairs added to sorted dictionary can be searched.
1. Adding key that exists overwrites the existing one.
1. Keys are sorted.
1. Searching for minimum key returns the smallest key.
1. Searching for non-existing key raises `KeyError`.
1. Deleting a key and then searching it raises `KeyError`

- Restrict keys to integers for simplicity. In general, anything hashable works.

## Coding the first property

Introduce Hypothesis.

### Coding the generator

```python
# test_sorted_dict.py
def some_key_value_tuples():
    """Generator for lists of key-value tuples.
    """
    some_keys = some.integers()
    some_values = some.binary()
    some_kvs = some.tuples(some_keys, some_values)
    return some.lists(some_kvs)
```

```python
# test_sorted_dict.py
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

### Coding the property

```python
# test_sorted_dict.py
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

## Making the property pass

### Binary search tree

```python
# tree.py
from dataclasses import dataclass
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
# tree.py

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

```python
# tree.py
def insert(tree: Tree, key, value):
    """
    Reference insertion algorithm from Introduction to Algorithms.
    Operates in-place.
    """
    y = None
    x = tree.root

    log.debug("Inserting key=%d, value=%s", key, value)

    while x is not None:
        y = x
        if key < x.key:
            x = x.left
        elif key > x.key:
            x = x.right
        else:
            x.value = value
            return

    z = Node(key=key, value=value, parent=y)
    if y is None:
        tree.root = z
    elif z.key < y.key:
        y.left = z
    else:
        y.right = z
```

```python
# tree.py
def search(tree: Tree, key):
    node = _search_node(tree, key)
    return node.value


def _search_node(tree: Tree, key) -> Node:
    if tree.root is None:
        raise KeyError("Empty dictionary, can't find key {}".format(key))

    x = tree.root

    while x is not None:
        if key < x.key:
            x = x.left
        elif key > x.key:
            x = x.right
        else:
            return x

    raise KeyError("Key {} not found".format(key))
```

### Sorted dictionary

```python
# sorted_dict.py
from . import tree

class SortedDict:
    def __init__(self):
        self._tree = tree.Tree()

    def __setitem__(self, key, item):
        tree.insert(self._tree, key, item)

    def __getitem__(self, key):
        return tree.search(self._tree, key)
```

## Coding invariant

```python
# test_sorted_dict.py
@given(dict_and_values=some_sorted_dicts())
def test_keys_sorted(dict_and_values):
    """Invariant: keys in sorted dictionary are sorted."""
    sorted_dict, _ = dict_and_values
    keys = sorted_dict.keys()
    assert keys == sorted(keys)
```

```python
# sorted_dict.py
class SortedDict:
    ...
    def keys(self):
        return list(self.keys_())

    def keys_(self):
        for key, _ in tree.collect(self._tree)
            yield key
```

```python
# tree.py
def collect(tree: Tree):
    if tree.root is None:
        return ()

    return _collect(tree.root)


def _collect(node: t.Optional[Node]):

    if node is None:
        return

    for key, value in _collect(node.left):
        yield key, value

    yield node.key, node.value

    for key, value in _collect(node.right):
        yield key, value
```

## Handling deletion

```python
# test_sorted_dict.py

@given(
    dict_and_values=some_sorted_dicts().filter(lambda drawn: len(drawn[1].keys()) > 0),
    data=some.data(),
)
def test_search_after_delete(dict_and_values, data):
    """
    Searching a key after deleting the key raises KeyError.
    """
    sorted_dict, expected = dict_and_values
    inserted_keys = list(expected.keys())
    key_to_delete = data.draw(some.sampled_from(inserted_keys), label="Key to delete")
    del sorted_dict[key_to_delete]
    with pytest.raises(KeyError):  # type: ignore
        sorted_dict[key_to_delete]
```

```python
# sorted_dict.py
class SortedDict:
    ...
    def __delitem__(self, key):
        return tree.delete(self._tree, key)
```

The implementation of `tree.delete` is left as an exercise to the reader.

## Final touch: add doctest

```ini
# pytest.ini
[pytest]
addopts = --doctest-modules
doctest_optionflags= NORMALIZE_WHITESPACE IGNORE_EXCEPTION_DETAIL
```

Tests now also collect the doctest from `sorted_dict.py`!

## Bonus: stateful testing

How to test complex states? You need stuff like this:

```python
# test_sorted_dict.py
def test_search_after_delete(dict_and_values, data):
    ...

    remaining_keys = sorted_dict.keys()

    assert len(remaining_keys) == len(inserted_keys) - 1

    assert remaining_keys == sorted(remaining_keys)
```

Enter stateful testing:

```python
# test_sorted_dict.py
class StatefulDictStateMachine(RuleBasedStateMachine):
    def __init__(self):
        super().__init__()
        self.sorted_dict = SortedDict()
        self.state = {}

    inserted_keys = Bundle("inserted")
    deleted_keys = Bundle("deleted_keys")

    @rule(target=inserted_keys, key=some.integers(), value=some.text())
    def insert(self, key, value):
        event("Inserting key")
        self.sorted_dict[key] = value
        self.state[key] = value

        return key

    @rule(key=inserted_keys)
    def search(self, key):
        # We may have deleted the key already if it was
        # a duplicate so check it should be there.
        assume(key in self.state)
        event("Searching existing key")
        assert self.sorted_dict[key] == self.state[key]

    @rule(key=consumes(inserted_keys))
    def delete(self, key):
        assume(key in self.state)
        event("Deleting key")
        del self.sorted_dict[key]
        del self.state[key]

    @rule(key=some.integers())
    def search_non_existing(self, key):
        assume(key not in self.state)
        event("Searching non-existing key")
        with pytest.raises(KeyError):  # type: ignore
            self.sorted_dict[key]

    @invariant()
    def keys_sorted(self):
        keys = self.sorted_dict.keys()
        assert keys == sorted(keys)


TestStatefulDict = StatefulDictStateMachine.TestCase
```

```bash
$ pytest -s -k TestStateful --hypothesis-show-statistics
... lots of output
  - Events:
    ...
    *  55.80%, Inserting key
    *  50.72%, Searching non-existing key
    *  31.16%, Deleting key
    ...
    *  17.39%, Searching existing key
```

### Conclusion

- Properties can drive development
- Generalize examples into properties and turn properties into property-based tests
- Positive vs. negative testing

### Resources

- [Property-Based Testing with PropEr, Erlang, and Elixir](https://propertesting.com/): Excellent book on property-based testing with a chapter on properties-driven development
- [From 1 to 10,000 test cases in under an hour: A beginner's guide to property-based testing](https://dev.to/meeshkan/from-1-to-10-000-test-cases-in-under-an-hour-a-beginner-s-guide-to-property-based-testing-1jf8): Guide to PBT from my colleagues Carolyn and Fredrik
- [Hypothesis Quick Start guide](https://hypothesis.readthedocs.io/en/latest/quickstart.html): Get started with property-based testing with Hypothesis
