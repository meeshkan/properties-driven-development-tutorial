"""Custom implementation of mutable dict supporting
minimum, maximum, predecessor, and successor operations.

Examples:

>>> tree = TreeDict()
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

from dataclasses import dataclass
from logging import getLogger, basicConfig
import typing as t

basicConfig(level="DEBUG")
log = getLogger(__name__)


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


@dataclass
class Tree:
    root: t.Optional["Node"] = None

    def __repr__(self):
        return "Tree with root: {}".format(repr(self.root))


def _inorder_walk(node: t.Optional[Node], func):
    if node is None:
        return
    _inorder_walk(node.left, func)
    func(node)
    _inorder_walk(node.right, func)


def insert_to(tree: Tree, key, value):
    """Reference insertion algorithm from Introduction to Algorithms. Operates in-place.
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


def transplant(tree: Tree, node1: Node, node2: t.Optional[Node]):
    log.debug("Transplanting node %s in-place of node %s", repr(node2), repr(node1))
    if node1.parent is None:
        tree.root = node2
    elif node1 == node1.parent.left:
        # Left child
        node1.parent.left = node2
    elif node1 == node1.parent.right:
        # Right child
        node1.parent.right = node2
    else:
        raise AssertionError(
            "Something horribly wrong in the tree, not a child of the parent"
        )

    if node2 is not None:
        node2.parent = node1.parent


def minimum(node: t.Optional[Node]) -> t.Optional[Node]:
    if node is None:
        return None

    while node.left is not None:
        node = node.left

    return node


def maximum(node: t.Optional[Node]) -> t.Optional[Node]:
    if node is None:
        return None

    while node.right is not None:
        node = node.right

    return node


def delete_node(tree: Tree, node: Node):
    if node.left is None:
        transplant(tree, node, node.right)
        return
    elif node.right is None:
        transplant(tree, node, node.left)
        return

    y = minimum(node.right)

    assert y is not None

    if y.parent != node:
        transplant(tree, y, y.right)
        y.right = node.right
        y.right.parent = y

    transplant(tree, node, y)
    y.left = node.left
    y.left.parent = y


def delete(tree: Tree, key: int):
    log.debug("Deleting key %d from tree", key)
    node = search_node(tree, key)
    delete_node(tree, node)


def search(tree: Tree, key):
    node = search_node(tree, key)
    return node.value


def search_node(tree: Tree, key) -> Node:
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


class TreeDict:
    def __init__(self):
        self.tree = Tree()

    def __setitem__(self, key, item):
        insert_to(self.tree, key, item)

    def __getitem__(self, key):
        return search(self.tree, key)

    def __delitem__(self, key):
        return delete(self.tree, key)

    def __contains__(self, key):
        try:
            self[key]
            return True
        except KeyError:
            return False

    def inorder_walk(self, func):
        _inorder_walk(self.tree.root, func)


__all__ = ["TreeDict"]
