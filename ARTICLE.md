---
title: Introduction to properties-driven development
description: Learn what property-driven development is and how to apply it for a project.
slug: introduction-to-properties-driven-development
date: 2020-04-17
authors: ["kimmo"]
tags:
  - testing
  - tutorial
  - beginners
  - python
---

> _This article was edited by [Carolyn Stransky](https://dev.to/carolstran). XXX and XXX are acknowledged for their valuable feedback._

### Intro alternative 1

Properties-driven development is the application of [property-based testing](https://dev.to/meeshkan/from-1-to-10-000-test-cases-in-under-an-hour-a-beginner-s-guide-to-property-based-testing-1jf8?utm_campaign=Software%2BTesting%2BWeekly&utm_source=Software_Testing_Weekly_14) in the context of test-driven development. While coding, we constantly write tests to ensure our code is easily testable and usable. Instead of relying on hard-coded inputs and outputs in our tests, we instead write _generators of test cases_ and ensure given _properties_ hold for our code.

Thinking in terms of properties forces us to be very explicit about what our code can and cannot do. We're effectively adopting a [design by contract](https://en.wikipedia.org/wiki/Design_by_contract) approach, which can immensely help in understanding the problem we're trying to solve before diving into coding.

In this article, we'll learn what properties-driven development looks like. We also apply the principles to develop a module for a sorted dictionary.

I recently learned about the concept from the [Property-Based Testing with PropEr, Erlang, and Elixir](https://propertesting.com/) book, so this article is heavily inspired by the contents of the book.

### Intro alternative 2

In his book [Thinking, Fast and Slow](), Daniel Kahneman describes the two modes of thought our brain uses. The first one is fast, instinctive, and emotional, and the second one is slower, more deliberate and more logical. The slow thinking mode is generally more appropriate for solving complex tasks.

Imagine you're given an interesting coding task. It's likely that the fast mode of thought activates. Based on years of experience of software development, your brain generates an idea of what the implementation should look like, and, based on that idea, it would be very tempting to jump into implementing it.

To avoid the fast mode taking over, you should slow down and think about the problem. What is the actual problem you're trying to solve? How is the user expected to gain value from your solution? For this, you need to think like a _user, not a developer_.

In day-to-day work, one tested way to think like a user is to write tests. Lots of tests. Tests are the first users of your code. It's not important whether you write tests before, during, or after the actual implementation, but they should guide the development. The authors of the [Pragmatic Programmer]() even go so far to say that _testing is not about finding bugs_.

However, writing good tests is hard. It may be easy to come up with happy-path examples where things just work, but it's much harder to come up with test cases stretching the boundaries of your code. Also, it's common have unconscious assumptions about your code that you put in your tests: You may test your code with "foo" and "bar" and therefore conclude it works with any String, but it might actually break horribly when fed with `"\U000f28d4\U0006ef7d"`.

Enter [property-based testing](https://dev.to/meeshkan/from-1-to-10-000-test-cases-in-under-an-hour-a-beginner-s-guide-to-property-based-testing-1jf8?utm_campaign=Software%2BTesting%2BWeekly&utm_source=Software_Testing_Weekly_14) (PBT). PBT is great for verifying assumptions about your code. If you think your code works with any string, you should let the computer generate a lot of test strings for you and see if it actually does work. Thinking in terms of properties such as _preconditions_, _postconditions_, and _invariants_ also forces you to **think** and explicitly state what your code can and cannot do. Such a [design by contract](https://en.wikipedia.org/wiki/Design_by_contract) approach can immensely help in understanding the problem you're trying to solve before diving into coding.

Properties-driven development is an approach that lets properties guide coding. In this article, we'll learn what properties-driven development is and how to apply it to guide the development of a custom dictionary datatype. I recently learned about the concept from the [Property-Based Testing with PropEr, Erlang, and Elixir](https://propertesting.com/) book, so this article is heavily inspired by the contents of the book.

## ToC

- What is properties-driven development?

- Example project: sorted dictionary

  - What should it do?
  - Listing requirements
  - Implementing insert and search
  - Implementing deletion
  - Ensuring keys are sorted
  - Stateful testing
  - Final touch: add `doctest`

- [Conclusion](#conclusion)
- [Resources](#resources)

⚠️ **Prerequisites**:

- A general understanding of software testing
- (Optional) [Python 3+](https://www.python.org/downloads/)\* if you want to follow along

_\* This guide will use Python for code examples, but the concepts aren't limited to any specific programming language. So even if you don't know Python, we'd encourage you to read along anyway._

💻 **References**:
This [GitHub repository](https://github.com/meeshkan/properties-driven-development-tutorial) contains all the featured code examples as tests. The repository also contains instructions for how to execute them.

## What is properties-driven development?

As mentioned in the introduction, properties-driven development is essentially _test-driven development_ in the context of _property-based testing_. Test-driven development asks us to think what our code should do and put that into a test. Property-based testing asks us to formulate that test in terms of _properties_.

For example, assume we're writing code for converting a [CSV](https://en.wikipedia.org/wiki/Comma-separated_values) into a [JSON](https://en.wikipedia.org/wiki/JSON) array. Instead of jumping into writing a CSV parser, test-driven development asks us to come up with test cases. Here's an example input:

```csv
a,b,c
3,2,1
6,3,2
```

This should be turned into the following JSON:

```json
[
  { "a": 3, "b": 2, "c": 1 },
  { "a": 6, "b": 3, "c": 2 }
]
```

This would make a nice unit test for our code! However, the test has quite a few assumptions baked within:

- Keys are distinct
- Values are integers
- There are no missing values

Being good developers we are, we would of course go on writing unit tests to cover each of those assumptions with the behaviour we want. The bad news is our imaginations are limited. For example, above we forgot to list the assumptions that the list of keys is non-empty and there's at least one row in the CSV.

Property-based tests are excellent for forcing us to be **explicit about our assumptions**. To come up with properties for our CSV-to-JSON parser, we would need to first generate CSVs we expect our parser to be able to handle. Here's the pseudocode for one such generator:

1. Generate keys: a list of arbitrary strings,
1. Generate the number of rows: a non-negative integer,
1. Generate rows: For each row and key, generate an arbitrary string value.

Can you see how many tricky cases our generator forces us to cover? The list of keys may be empty, the number of rows may be zero, and we assume our code works with arbitrary strings (including empty strings and strings containing commas) both as keys and values. Generator as above would push our CSV parser to its limits!

The generator as above might turn out to be too demanding for our use case. If that happens, we can simply relax the generator to produce "friendlier" data. Instead of "programming by coincidence", where specific cases may or may not be supported, we've consciously made the decision which cases are supported.

The above generator is an example of a "bottom-up" approach to data generation. Instead of generating totally random CSVs, we generate them bottom-up, keeping track of what goes in so that we know what our expected result is. This avoids the problem where we need to duplicate the implementation in tests. For example, with the generator above, we know the length of the resulting JSON array should be equal to the non-negative integer drawn at step 2, the number of rows we generated. That's a good property!

This concludes the brief introduction to properties-driven development. We next move to applying the principles in an example project.

## Example project: sorted dictionary

As an example project, we'll build our own **sorted dictionary** in Python. We call the datastructure `SortedDict` and expect it to always keep its keys in sorted order. Such a `SortedDict` might be useful for keeping, for example, users in the order they logged into our application. We're also able to traverse the sorted list of key-value pairs in linear time.

We keep the keys sorted by storing the key-value pairs in a [binary search tree](https://en.wikipedia.org/wiki/Binary_search_tree). Because the standard tree could be unbalanced and therefore ineffective, you should use [`sortedcontainers`](https://github.com/grantjenks/python-sortedcontainers/) in real-life use cases.

Implementing sorted dictionary still makes a good example for properties-driven development for various reasons. First, it shows that property-based testing is not only for functional programming but just as useful for implementing a mutable dictionary. Second, while the implementation is straight-forward, it's also complex enough to deserve good tests. Especially the deletion logic is error-prone. Finally, because the implementation is based on the well-known binary search tree, we can resort to simple reference implementations in this article.

For the simplicity of this article, we assume the keys are integers and that the keys themselves are used for comparison (instead of providing a custom callable per value like `SortedDict` in `sortedcontainers` does).

### What should it do?

To come up with properties, we first need to come up with the requirements for our `SortedDict`. One way to come up with requirements is to play around with the API we expect our module to have.

First, we probably expect we can search for an inserted key:

```python
>>> # Insert and search
>>> sorted_dict = SortedDict()
>>> sorted_dict[2] = 'two'
>>> sorted_dict[2]
'two'
```

We also expect keys are always sorted irrespective of the insertion order. Continuing on above:

```python
>>> # Keys are sorted
>>> sorted_dict[1] = 'one'
>>> sorted_dict.keys()
[1, 2]
```

Like with the standard dictionary, we expect re-inserting an existing key will result in the value being overwritten:

```python
>>> # Handles duplicate keys
>>> sorted_dict[2] = 'two-two'
>>> sorted_dict[2]
'two-two'
```

We expect searching for a non-existing key raises `KeyError`:

```python
>>> # Non-existing key
>>> sorted_dict[3]
Traceback (most recent call last):
KeyError: ...
```

Finally, if we delete a key, we know searching for it will raise a `KeyError`:

```python
>>> # Searching for deleted key
>>> del sorted_dict[1]
>>> sorted_dict[1]
Traceback (most recent call last):
KeyError: ...
```

### Listing requirements

Now that we have a grasp for what we expect our code to do, we can try to generalize the examples above into requirements:

1. Key-value pairs added to sorted dictionary can be searched.
1. Adding key that exists overwrites the existing one.
1. Keys are always sorted.
1. Searching for non-existing key raises `KeyError`.
1. Deleting a key and then searching it raises `KeyError`

Such requirements serve as the basis for **properties**. Next, we'll first write a property for the first requirement: one can insert key-value pairs into the dictionary and then search for them.

### Implementing insert and search

We'll use the [Hypothesis](https://hypothesis.readthedocs.io/) library for writing properties for our sorted dictionary. Hypothesis supports generating [almost any kind of data](https://hypothesis.readthedocs.io/en/latest/data.html) you can imagine and provides simple decorators for writing property-based testing.

To be able to write properties, we first write the basic skeleton for `SortedDict`:

```python
# sorted_dict.py
class SortedDict:
    def __init__(self):
        pass

    def __setitem__(self, key, item):
        pass

    def __getitem__(self, key):
        pass
```

The `__setitem__` method is called when `sorted_dict[key] = item` is invoked. Similarly, `__getitem__` defines the behaviour for `sorted_dict[key]`.

Before going any further in the implementation, we write down the property. Proceeding one step at a time like this is a good way to ensure our tests work as expected: once we're done writing a test, we make sure it fails before getting into implementation.

#### Generator

To get started with the property, we need a generator of key-value tuples. Here's how to do it in Hypothesis:

```python
# test_sorted_dict.py
import hypothesis.strategies as some

def some_key_value_tuples():
    """
    Generator for lists of key-value tuples.
    """
    some_keys = some.integers()
    some_values = some.binary()
    some_kvs = some.tuples(some_keys, some_values)
    return some.lists(some_kvs)
```

We alias `hypothesis.strategies` as `some` as it reads nicely. The function first defines a generator `some_keys` for keys, which we assume to be integers. For values, we assume any binary is valid. We then create a generator of key-value tuples and, using that, a generator of lists of tuples.

To see what data this generator can generate, we can call `some_key_value_tuples().example()`:

```python
>>> some_key_value_tuples().example()
[]
>>> some_key_value_tuples().example()
[(53, b'{\x8b\xed\x92\xa8\xcb\x7fq\x95')]
>>> some_key_value_tuples().example()
[(-19443, b'\x16ERa'), (-425, b'')]
```

Having a generator for lists of key-value tuples, we wish to build a `SortedDict` instance containing those tuples. With Hypothesis, we can use [`hypothesis.strategies.composite`](https://hypothesis.readthedocs.io/en/latest/data.html#hypothesis.strategies.composite) to compose generators as follows:

```python
# test_sorted_dict.py
@some.composite
def some_sorted_dicts(draw):
    """
    Generator of sorted dicts.
    """
    key_values = draw(some_key_value_tuples())

    sorted_dict = SortedDict()
    for key, val in key_values:
        sorted_dict[key] = val
    return sorted_dict
```

The `draw` function injected by `composite` can be used to draw values from another generator to derive new data. Above, we draw a list of key-value tuples and then insert of key-value pairs into our `SortedDict` (we define `SortedDict` in a moment).

While `some_sorted_dicts` defined above generates instances of `SortedDict`, there's a problem: we don't know what data went into creating the sorted dictionary. To do that, we'll store the key-value pairs in a standard Python dictionary as follows:

```python
# test_sorted_dict.py
@some.composite
def some_sorted_dicts(draw):
    """
    Generator of sorted dicts. Returns a tuple of the sorted dictionary and a dictionary holding the key-value pairs used for data generation.
    """
    # ... define sorted_dict as as above

    expected = {}
    for key, val in key_values:
        expected[key] = val

    return sorted_dict, expected
```

The variable `expected` contains the key-value pairs we expect to find from our sorted dictionary. It acts as a simplified "model" for sorted dictionary with the exception that its keys are not sorted. Using a standard dictionary as the model is useful also because it handles duplicates in the same way as we expect `SortedDict` to handle them (overwrite).

#### Property

Having the test case generator `some_sorted_dicts` defined, we're ready to state our first property: that any keys inserted into the dictionary can be searched.

```python
# test_sorted_dict.py
from hypothesis import given

@given(dict_and_values=some_sorted_dicts())
def test_insert_and_search(dict_and_values):
    """
    Key-value pairs added to sorted dictionary can be searched.
    """
    sorted_dict, expected = dict_and_values

    for key, value in expected.items():
        in_dict = sorted_dict[key]
        assert in_dict == value
```

Test case is marked as Hypothesis test with the `@given` decorator. When this test is run, Hypothesis will generate 100 different sorted dictionaries and verify that all key-value pairs expected to be found in the dictionary are found.

If we run the tests now, they should fail: we need to implement `__setitem__` and `__getitem__`. For those, we need the binary search tree.

#### Binary search tree

For the binary search tree, we use the implementation from [Introduction to Algorithms](https://en.wikipedia.org/wiki/Introduction_to_Algorithms) book. Because the implementation is not that important for the purposes of this article, we proceed quickly.

`Tree` is defined as a [dataclass](https://docs.python.org/3/library/dataclasses.html) as follows:

```python
# tree.py
from dataclasses import dataclass
import typing as t

@dataclass
class Tree:
    """
    Binary search tree.
    """

    root: t.Optional[Node] = None

    def __repr__(self):
        return "Tree(root={})".format(repr(self.root))
```

Tree has only one attribute, `root`. If the tree is empty, `root` is equal to `None`. Otherwise, it contains a `Node` defined like this:

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
        return "Node(key={}, value={}, left=({}), right=({})".format(
            self.key, repr(self.value), repr(self.left), repr(self.right)
        )
```

A node has a key and a value. It also contains references to its left and right children as well as its parent. Note that `parent` is not included in `__repr__` to avoid infinite loops (printing a child prints the parent, which prints the child, which prints the parent...).

Inserting key and a value to the tree happens as follows:

```python
# tree.py
def insert(tree: Tree, key, value):
    """
    Reference insertion algorithm from Introduction to Algorithms.
    Operates in-place.
    """
    y = None
    x = tree.root

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

Note that if key is equal to an existing key, the value in the corresponding node is updated in-place.

Searching from the tree is straightforward, going down the tree until finding a match or, if no match is found, raising `KeyError`:

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

Search involves a helper function that searches a `Node` by key. We'll need this when implementing deletion.

#### Putting it all together

With the tree supporting insert and search, we can use the tree in our `SortedDict`:

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

If we now run the property-based test for insertion and search, we should see it pass with flying colors!

We have now implemented the first requirement with a property-based test. Let's take a look at our remaining requirements:

1. ~~Key-value pairs added to sorted dictionary can be searched.~~
1. Adding key that exists overwrites the existing one.
1. Keys are always sorted.
1. Searching for non-existing key raises `KeyError`.
1. Deleting a key and then searching it raises `KeyError`

We could also consider requirement 2 be checked if we trust Hypothesis to generate duplicate keys. We could work on the requirement of keeping keys sorted, but we actually want that to hold also after deletions, as that's the trickiest operation. We'll therefore handle requirement 5 next.

### Implementing deletion

The requirement states that searching for a deleted key raises `KeyError`. How can we put that into a property? An easy way is to use our `some_sorted_dicts()` generator from above and let Hypothesis draw one of the keys for deletion. We then delete that key and ensure searching raises `KeyError`.

To draw a key to delete, we could again use `composite` to create a composite strategy yielding a sorted dictionary, the dictionary of expected contents, and a key to delete. However, in this case it's simpler to use [`data`](https://hypothesis.readthedocs.io/en/latest/data.html#hypothesis.strategies.data) strategy from Hypothesis to draw _during the test_.

Here's what that would look like:

```python
# test_sorted_dict.py

@given(
    dict_and_values=some_sorted_dicts(),
    data=some.data(),
)
def test_search_after_delete(dict_and_values, data):
    """
    Searching a key after deleting the key raises KeyError.
    """
    sorted_dict, expected = dict_and_values
    inserted_keys = list(expected.keys())
    some_key = some.sampled_from(inserted_keys)
    key_to_delete = data.draw(some_key, label="Key to delete")
    del sorted_dict[key_to_delete]
    with pytest.raises(KeyError):  # type: ignore
        sorted_dict[key_to_delete]
```

We first create a generator `some_key` for sampling from the list of inserted keys. We can then use `data.draw()` to draw from the generator interactively. Once a key is drawn, we delete the key and verify searching for it raises `KeyError`.

However, there's one problem in our implementation. The list of inserted keys may be empty. We need to cover for that case by ensuring the test only runs for non-empty dictionaries. We can do that by using `filter` in our generator:

```python
# test_sorted_dict.py

@given(
    dict_and_values=some_sorted_dicts().filter(lambda drawn: len(drawn[1]) > 0),
    data=some.data(),
)
def test_search_after_delete(dict_and_values, data):
    ...
```

The filter ensures that the dictionary is non-empty.

With the property ready, we can move to implementation. The `del sorted_dict[key]` actually means `sorted_dict.__delitem__(key)`, so we define `__delitem__` in `SortedDict`:

```python
# sorted_dict.py
class SortedDict:
    ...
    def __delitem__(self, key):
        return tree.delete(self._tree, key)
```

We again delegate the deletion to the tree with `tree.delete` function. Because the deletion is somewhat tricky but standard, we refer to the accompanying repository for its implementation.

Our list of requirements now looks as following:

1. ~~Key-value pairs added to sorted dictionary can be searched.~~
1. ~~Adding key that exists overwrites the existing one.~~
1. Keys are always sorted.
1. Searching for non-existing key raises `KeyError`.
1. ~~Deleting a key and then searching it raises `KeyError`~~

As our last example, we write a property for the keys being always sorted.

### Ensuring keys are sorted

A property such as "Keys are always sorted" is an invariant: Whatever operations are performed, it remains true. Ensuring all the dictionaries we generate have sorted keys is straightforward:

```python
# test_sorted_dict.py
@given(dict_and_values=some_sorted_dicts())
def test_keys_sorted(dict_and_values):
    """
    Invariant: keys in sorted dictionary are sorted.
    """
    sorted_dict, _ = dict_and_values
    keys = sorted_dict.keys()
    assert keys == sorted(keys)
```

Again, we refer the implementation to the accompanying repository.

While the property above ensures that keys are always sorted after inserting keys, the property should also be checked after deletion. Therefore, we should also check the invariant holds in our deletion property above:

```python
# test_sorted_dict.py

@given(
    dict_and_values=some_sorted_dicts().filter(lambda drawn: len(drawn[1]) > 0),
    data=some.data(),
)
def test_search_after_delete(dict_and_values, data):
    ...
    keys = sorted_dict.keys()
    assert keys == sorted(keys)
```

While this works, there's something unsatisfactory about it. The premise of property-based testing is that we can cover all kinds of unexpected cases. Here, we're hard-coding the cases where the invariant should be tested. Is there something we can do to randomize testing the invariant?

Enter [stateful testing](https://hypothesis.readthedocs.io/en/latest/stateful.html). With stateful tests, we define operations that can be run but leave their order for the framework to decide.

In Hypothesis, one can use [`RuleBasedStateMachine`]() for that. We won't go into details, but here's an example for `SortedDict`:

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

The methods defined in our `RuleBasedStateMachine` decorated with `@rule` define the "commands" the state machine runs. The decorator `@invariant` ensures that the keys being sorted is checked after every command. We also keep a "model" of our current expected state in `self.state` to know what keys our `SortedDict` is expected to contain.

Stateful tests such as above can work wonders for revealing tricky bugs. They can, however, be very hard to debug, so always try to cover as many cases as possible with regular unit and property-based tests.

## Final touch: add doctest

Remember how we played around with the expected API of our `SortedDict` to come up with the properties? For example, we assumed the following would hold:

```python
>>> # Insert and search
>>> sorted_dict = SortedDict()
>>> sorted_dict[2] = 'two'
>>> sorted_dict[2]
'two'
```

It would be great to ensure these simple examples hold also for our implementation. Writing properties can sometimes be complex and error-prone, so it's very valuable to have such human-readable examples serve as "anchors". They ensure that no matter what happens, our code works as expected at least with the simplest example inputs.

Such tests serve as documentation, and therefore they make excellent [doctests](https://docs.python.org/3/library/doctest.html). We can add the tests at the top of our `sorted_dict.py` module in a docstring:

```python
# sorted_dict.py
"""
Sorted, mutable dictionary
keeping keys in sorted order.

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
...
"""
```

In `pytest`, we can enable doctests with the `--doctest-modules` flag. Add the following in `pytest.ini` to always run doctests:

```ini
# pytest.ini
[pytest]
addopts = --doctest-modules
doctest_optionflags= NORMALIZE_WHITESPACE IGNORE_EXCEPTION_DETAIL
```

The second line configures doctest to ignore extraneous whitespaces and exception details.

When `pytest` is run, it now also runs the examples from the documentation.

## Conclusion

In this article, we learned how to apply property-based testing in the context of test-driven development and how to apply it to developing a sorted dictionary. Thinking in properties instead of concrete examples can help you slow down and be precise about what your code is expected to do and what not. However, remember that property-based testing _does not replace regular unit tests_: instead, it provides a new tool to our testing toolboxes. Sometimes, property-based testing is simply not the right tool for the job: for an interesting article on when property-based testing shines, take a look at this [article](https://medium.com/erlang-battleground/property-based-testing-erlang-elixir-de72ad24966b).

Thank you for reading, as always I would be happy to hear your feedback!

### Resources

- [Property-Based Testing with PropEr, Erlang, and Elixir](https://propertesting.com/): Excellent book on property-based testing with a chapter on properties-driven development
- [From 1 to 10,000 test cases in under an hour: A beginner's guide to property-based testing](https://dev.to/meeshkan/from-1-to-10-000-test-cases-in-under-an-hour-a-beginner-s-guide-to-property-based-testing-1jf8): Guide to PBT from my colleagues Carolyn and Fredrik
- [Hypothesis Quick Start guide](https://hypothesis.readthedocs.io/en/latest/quickstart.html): Get started with property-based testing with Hypothesis in Python
- [My Take on Property-Based Testing](https://medium.com/erlang-battleground/property-based-testing-erlang-elixir-de72ad24966b): Insights on when to use property-based testing
- [Property-Based Test-Driven Development in Elixir](https://medium.com/grandcentrix/property-based-test-driven-development-in-elixir-49cc70c7c3c4): Mathias Polligkeit's article on properties-driven development
