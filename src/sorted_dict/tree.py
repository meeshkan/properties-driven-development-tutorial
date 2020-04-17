"""Binary search tree.
"""

from dataclasses import dataclass
from logging import getLogger
import typing as t

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
    """Binary search tree.
    """

    root: t.Optional["Node"] = None

    def __repr__(self):
        return "Tree with root: {}".format(repr(self.root))


def walk(tree: Tree, func):
    if tree.root is None:
        return

    _inorder_walk(tree.root, func)


def _inorder_walk(node: t.Optional[Node], func):
    if node is None:
        return
    _inorder_walk(node.left, func)
    func(node)
    _inorder_walk(node.right, func)


def insert(tree: Tree, key, value):
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


def _transplant(tree: Tree, node1: Node, node2: t.Optional[Node]):
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


def minimum(tree: Tree) -> int:
    if tree.root is None:
        raise ValueError("No minimum in empty tree")

    min_node = _minimum_node(tree.root)

    assert min_node is not None

    return min_node.key


def maximum(tree: Tree) -> int:
    if tree.root is None:
        raise ValueError("No maximum in empty tree")

    max_node = _maximum_node(tree.root)

    assert max_node is not None

    return max_node.key


def _minimum_node(node: t.Optional[Node]) -> t.Optional[Node]:
    if node is None:
        return None

    while node.left is not None:
        node = node.left

    return node


def _maximum_node(node: t.Optional[Node]) -> t.Optional[Node]:
    if node is None:
        return None

    while node.right is not None:
        node = node.right

    return node


def _delete_node(tree: Tree, node: Node):
    if node.left is None:
        _transplant(tree, node, node.right)
        return
    elif node.right is None:
        _transplant(tree, node, node.left)
        return

    y = _minimum_node(node.right)

    assert y is not None

    if y.parent != node:
        _transplant(tree, y, y.right)
        y.right = node.right
        y.right.parent = y

    _transplant(tree, node, y)
    y.left = node.left
    y.left.parent = y


def delete(tree: Tree, key: int):
    log.debug("Deleting key %d from tree", key)
    node = _search_node(tree, key)
    _delete_node(tree, node)


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


__all__ = ["Tree", "insert", "search", "delete", "walk", "minimum", "maximum"]
