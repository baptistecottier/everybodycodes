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
    A node with its plug and its two sockets, each given as (colour, shape),
    and the nodes plugged into its left and right sockets.
    """
    node_id: int
    plug: tuple[str, str]
    left_socket: tuple[str, str]
    right_socket: tuple[str, str]
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
        nodes: list[Node] = []
        for line in pi.splitlines():
            details: None | Result | Match = parse(
                "id={:d}, plug={} {}, leftSocket={} {},"
                " rightSocket={} {}, data={}",
                line
            )
            if not isinstance(details, Result):
                raise ValueError("Invalid input format")
            node_id, pc, ps, lc, ls, rc, rs, _ = details.fixed
            nodes.append(Node(node_id, (pc, ps), (lc, ls), (rc, rs)))
        parts_inputs.append(nodes)
    return parts_inputs


def solver(content: list[list[Node]]) -> Iterator[int]:
    """
    Solve all puzzle parts for this quest.
    """
    yield build_tree(content[0], strong=True, weak=False).checksum()
    yield build_tree(content[1], strong=False, weak=True).checksum()
    yield build_tree(content[2], strong=True, weak=True).checksum()


def place(
    to_place: Node,
    node: Node,
    strong: bool,
    weak: bool
) -> tuple[bool, Node]:
    """
    Walk the tree rooted at node (left socket, left subtree, right socket,
    right subtree) and plug to_place into the first socket it matches. When it
    detaches a weakly bonded node, carry on the walk with the detached node.
    Return whether the carried node was plugged, and the carried node.
    """
    result, detached_node = match(
        node.left_plug, node.left_socket, to_place.plug, strong, weak)
    if result:
        node.left_plug = to_place
        if detached_node is None:
            return (True, to_place)
        to_place = detached_node

    elif node.left_plug is not None:
        placed, to_place = place(to_place, node.left_plug, strong, weak)
        if placed:
            return (True, to_place)

    result, detached_node = match(
        node.right_plug, node.right_socket, to_place.plug, strong, weak)
    if result:
        node.right_plug = to_place
        if detached_node is None:
            return (True, to_place)
        return (False, detached_node)

    if node.right_plug is not None:
        return place(to_place, node.right_plug, strong, weak)

    return (False, to_place)


def match(
    plugged: Node | None,
    socket: tuple[str, str],
    plug: tuple[str, str],
    strong: bool,
    weak: bool
) -> tuple[bool, Node | None]:
    """
    Whether a plug can go into a socket holding plugged, and the node it
    detaches. A free socket accepts a weak bond (colour or shape matching)
    when weak is set, otherwise only a strong one (both matching). When both
    strong and weak are set, a strong bond also detaches a weakly bonded node.
    """
    score = sum(s == p for s, p in zip(socket, plug))
    if plugged is None:
        return (score >= (2 - weak), None)
    if strong and weak and plugged.plug != socket and score == 2:
        return (True, plugged)
    return (False, None)


def build_tree(nodes: list[Node], strong: bool, weak: bool) -> Node:
    """
    Build a tree from the first node by plugging in each following node,
    walking again from the root while a detached node is left to plug.
    """
    tree = nodes[0]
    for node in nodes[1:]:
        placed = False
        while not placed:
            placed, node = place(node, tree, strong, weak)
    return tree
