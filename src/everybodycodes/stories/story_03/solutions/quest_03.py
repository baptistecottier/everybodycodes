"""
Story: Melody Made of Code
Quest: Plug and Play
"""

from dataclasses import dataclass
from typing import Iterator

from parse import Match, parse, Result  # type: ignore


@dataclass
class Node:
    """
    A node with its plug and its two sockets, each given as "COLOUR SHAPE",
    and the nodes plugged into its left and right sockets.
    """
    node_id: int
    plug: str
    left_socket: str
    right_socket: str
    left_plug: "Node | None" = None
    right_plug: "Node | None" = None

    def in_order(self) -> Iterator[int]:
        """
        Yield the node ids in order: left subtree, node, right subtree.
        """
        if self.left_plug is not None:
            yield from self.left_plug.in_order()
        yield self.node_id
        if self.right_plug is not None:
            yield from self.right_plug.in_order()

    def checksum(self) -> int:
        """
        Sum of each node id multiplied by its rank in the in-order walk.
        """
        return sum(
            rank * node_id for rank, node_id in enumerate(self.in_order(), 1))


def preprocessing(
    puzzle_inputs: dict[int, str]
) -> list[list[Node]]:
    """
    Parse each part into its list of nodes, in input order.
    """
    parts_inputs: list[list[Node]] = []

    for pi in puzzle_inputs.values():
        tree: list[Node] = []
        for node in pi.splitlines():
            details: None | Result | Match = parse(
                "id={:d}, plug={}, leftSocket={},"
                " rightSocket={}, data={}",
                node
            )
            if not isinstance(details, Result):
                raise ValueError("Invalid input format")
            tree.append(Node(*details.fixed[:-1]))
        parts_inputs.append(tree)
    return parts_inputs


def solver(content: list[list[Node]]) -> Iterator[int]:
    """
    Solve all puzzle parts for this quest.
    """
    yield build_tree(content[0], 1).checksum()
    yield build_tree(content[1], 2).checksum()
    yield build_tree(content[2], 3).checksum()


def place(to_place: Node, node: Node, level: int) -> tuple[bool, Node]:
    """
    Walk the tree rooted at node (left socket, left subtree, right socket,
    right subtree) and plug to_place into the first socket it matches. When it
    detaches a weakly bonded node, carry on the walk with the detached node.
    Return whether the carried node was plugged, and the carried node.
    """
    r, n = match(node.left_plug, node.left_socket, to_place.plug, level)
    if r:
        node.left_plug = to_place
        if n is None:
            return (True, to_place)
        to_place = n

    elif node.left_plug is not None:
        placed, to_place = place(to_place, node.left_plug, level)
        if placed:
            return (True, to_place)

    r, n = match(node.right_plug, node.right_socket, to_place.plug, level)
    if r:
        node.right_plug = to_place
        if n is None:
            return (True, to_place)
        return (False, n)

    if node.right_plug is not None:
        return place(to_place, node.right_plug, level)

    return (False, to_place)


def match(  # pylint: disable=too-many-return-statements
    plug_a: Node | None,
    node_a: str,
    node_b: str,
    level: int
) -> tuple[bool, Node | None]:
    """
    Whether a plug can go into a socket already holding plug_a, and the node
    it detaches. Only a free socket accepts it at levels 1 and 2: with both
    colour and shape matching at level 1, either of them at level 2. At level
    3, a free socket follows level 2, and a weakly bonded node is detached by
    a plug matching both colour and shape.
    """
    if plug_a is not None and level < 3:
        return (False, None)
    if level == 1:
        return (node_a == node_b, None)
    if level == 2:
        return (any(
            a == b for a, b in zip(node_a.split(' '), node_b.split(' '))),
            None)
    if level == 3:
        if plug_a is None:
            return match(plug_a, node_a, node_b, 2)
        if plug_a.plug == node_a:
            return (False, None)
        if node_a == node_b:
            return (True, plug_a)
    return (False, None)


def build_tree(nodes: list[Node], level: int) -> Node:
    """
    Build a tree from the first node by plugging in each following node,
    walking again from the root while a detached node is left to plug.
    """
    tree = nodes.pop(0)
    while nodes:
        node = nodes.pop(0)
        placed, node = place(node, tree, level)
        while not placed:
            placed, node = place(node, tree, level)
    return tree
