"""
Story: Melody Made of Code
Quest: Plug and Play
"""

from dataclasses import dataclass
from typing import Iterator

from parse import Match, parse, Result. # type: ignore


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

    def checksum(self, order: list[int]) -> int:
        """
        Collect the node ids in order (left subtree, node, right subtree)
        and return the sum of each id multiplied by its rank.
        """
        node = self
        if node.left_plug is not None:
            node.left_plug.checksum(order)
        else:
            if self.node_id not in order:
                order.append(node.node_id)
            if node.right_plug is not None:
                node.right_plug.checksum(order)

        if self.node_id not in order:
            order.append(node.node_id)
        if node.right_plug is not None:
            node.right_plug.checksum(order)

        return sum(n * rank for n, rank in enumerate(order, 1))


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
    yield build_tree(content[0], 1).checksum([])
    yield build_tree(content[1], 2).checksum([])


def place(to_place: Node, node: Node, level: int) -> bool:
    """
    Plug a node into the first socket it matches in the tree rooted at node.
    """
    if node.left_plug is None:
        if match(node.left_socket, to_place.plug, level):
            node.left_plug = to_place
            return True

    if node.left_plug is not None and place(to_place, node.left_plug, level):
        return True

    if node.right_plug is None:
        if match(node.right_socket, to_place.plug, level):
            node.right_plug = to_place
            return True

    if node.right_plug is not None:
        return place(to_place, node.right_plug, level)

    return False


def match(node_a: str, node_b: str, level: int) -> bool:
    """
    Whether a socket and a plug match: both colour and shape at level 1,
    colour or shape at level 2.
    """
    if level == 1:
        return node_a == node_b
    if level == 2:
        return any(
            a == b for a, b in zip(node_a.split(' '), node_b.split(' ')))
    return False


def build_tree(nodes: list[Node], level: int) -> Node:
    """
    Build a tree from the first node by plugging in each following node.
    """
    tree = nodes.pop(0)
    while nodes:
        node = nodes.pop(0)
        place(node, tree, level)
    return tree
