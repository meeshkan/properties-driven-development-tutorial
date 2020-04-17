from sorted_dict import SortedDict
from hypothesis import given, assume
from hypothesis.stateful import RuleBasedStateMachine, rule, Bundle, consumes, invariant
import hypothesis.strategies as some
import itertools
import pytest


def some_key_values():
    """Generator for lists of key-value tuples.
    """
    some_keys = some.integers()
    some_values = some.binary()
    some_kvs = some.tuples(some_keys, some_values)
    return some.lists(some_kvs)


def dedupe(key_value_pairs):
    """Remove duplicate keys by always picking the last. Also sorts the array by key.
    
    >>> dedupe([(0, 0), (0, 1), (1, 2), (0, 2)])
    [(0, 2), (1, 2)]
    
    """
    as_sorted = sorted(key_value_pairs, key=lambda pair: pair[0])
    grouped = itertools.groupby(as_sorted, lambda pair: pair[0])

    deduped = []
    for _, same_key in grouped:
        last = None
        for key_val in same_key:
            last = key_val
        deduped.append(last)
    return deduped


@some.composite
def some_sorted_dicts(draw):
    """Generator of sorted dicts along with the dictionary of
    key-value pairs used for constructing it."""
    key_values = draw(some_key_values())

    tree = SortedDict()
    for key, val in key_values:
        tree[key] = val

    expected = {}
    for key, val in key_values:
        expected[key] = val

    return tree, expected


@given(dict_and_values=some_sorted_dicts())
def test_insert_and_search(dict_and_values):
    sorted_dict, expected = dict_and_values

    for key, value in expected.items():
        in_dict = sorted_dict[key]
        assert in_dict == value, "Expected {} for key {}, got {}".format(
            value, key, in_dict
        )


@given(dict_and_values=some_sorted_dicts(), data=some.data())
def test_search_nonexisting(dict_and_values, data):
    """Test drawing a key not in dictionary."""
    sorted_dict, expected = dict_and_values
    inserted_keys = list(expected.keys())
    new_key = data.draw(some.integers())
    assume(new_key not in inserted_keys)

    with pytest.raises(KeyError):  # type: ignore
        sorted_dict[new_key]


@given(
    dict_and_values=some_sorted_dicts().filter(lambda drawn: len(drawn[1].keys()) > 0),
    data=some.data(),
)
def test_search_after_delete(dict_and_values, data):
    """Test drawing a key not in dictionary."""
    sorted_dict, expected = dict_and_values
    inserted_keys = list(expected.keys())
    key_to_delete = data.draw(some.sampled_from(inserted_keys), label="Key to delete")
    del sorted_dict[key_to_delete]
    with pytest.raises(KeyError):  # type: ignore
        sorted_dict[key_to_delete]


class StatefulDictStateMachine(RuleBasedStateMachine):
    def __init__(self):
        super().__init__()
        self.sorted_dict = SortedDict()
        self.in_dict = {}

    inserted_keys = Bundle("inserted")
    deleted_keys = Bundle("deleted_keys")

    @rule(target=inserted_keys, key=some.integers(), v=some.text())
    def insert(self, key, v):
        self.sorted_dict[key] = v
        self.in_dict[key] = v
        return key

    @rule(key=inserted_keys)
    def search(self, key):
        assert self.sorted_dict[key] == self.in_dict[key]

    @rule(key=consumes(inserted_keys))
    def delete(self, key):
        assume(key not in self.in_dict)
        del self.sorted_dict[key]
        del self.in_dict[key]

    @rule(key=some.integers())
    def search_non_existing(self, key):
        assume(key not in self.in_dict)
        with pytest.raises(KeyError):  # type: ignore
            self.sorted_dict[key]

    @invariant()
    def keys_sorted(self):
        keys = list(self.sorted_dict.keys())
        assert keys == sorted(keys)


TestStatefulDict = StatefulDictStateMachine.TestCase
