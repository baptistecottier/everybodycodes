"""
Story: Echoes of Enigmatus
Quest: Tangled Trees
"""

from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Iterator

from parse import parse, Match, Result  # type: ignore[import-untyped]


@dataclass
class Node:
    """
    Represents a binary tree node with an id, a value and letter.
    """
    node_id: int
    value: int
    letter: str
    right: "Node | None" = None
    left: "Node | None" = None

    def add_node(self, new_node: "Node") -> None:
        """
        Recursively inserts a new node into the binary search tree.
        """
        node: Node = self
        while True:
            if new_node.value > node.value:
                if node.right is None:
                    node.right = new_node
                    break
                node = node.right
            else:
                if node.left is None:
                    node.left = new_node
                    break
                node = node.left


def preprocessing(
    puzzle_inputs: dict[int, str]
) -> list[tuple[Node | None, Node | None]]:
    """
    Load and parse puzzle input from test or input file.
    """
    parts_inputs: list[tuple[Node | None, Node | None]] = []
    for part, pi in puzzle_inputs.items():
        commands: list[str] = pi.splitlines()
        parts_inputs.append(build_trees(commands, part))
    return parts_inputs


def solver(
    trees_nodes: list[tuple[Node | None, Node | None]]
) -> Iterator[str]:
    """
    Solves the puzzle by building trees and finding the maximum word at each
    depth level.
    """
    for lt, rt in trees_nodes:
        yield find_max_word(lt) + find_max_word(rt)


def build_trees(
    commands: list[str],
    part: int
) -> tuple[Node, Node]:
    """
    Builds left and right binary search trees from commands and applies swaps.
    """
    left_tree, right_tree = nodes_from_data(commands[0])
    patterns: list[str] = ["value", "letter"]
    if part == 3:
        patterns += ["left", "right"]
    for node in commands[1:]:
        if node.startswith("SWAP"):
            swap(left_tree, right_tree, int(node.split()[1]), patterns)
            continue
        left_node, right_node = nodes_from_data(node)
        right_tree.add_node(right_node)
        left_tree.add_node(left_node)
    return (left_tree, right_tree)


def find_max_word(
    tree: Node | None
) -> str:
    """
    Find the longest word at any depth level in the binary tree.
    """
    queue = deque([(0, tree)])
    depths: dict[int, list[str]] = defaultdict(list)
    while queue:
        d, node = queue.popleft()
        if node is None:
            continue
        depths[d].append(node.letter)
        queue += [(d + 1, node.left), (d + 1, node.right)]
    letters = max(depths.values(), key=len)
    return "".join(letters)


def nodes_from_data(line: str) -> tuple[Node, Node]:
    """
    Parse a line and create left and right tree nodes from the data.
    """
    result: None | Result | Match = parse(
        "ADD id={:d} left=[{:d},{}] right=[{:d},{}]", line
    )
    if isinstance(result, Result):
        node_id, lv, ll, rv, rl = result
        left_tree = Node(node_id, lv, ll, None, None)
        right_tree = Node(node_id, rv, rl, None, None)
        return left_tree, right_tree
    raise ValueError("Invalid input format")


def swap(
    ltree: Node | None,
    rtree: Node | None,
    target: int,
    attributes: list[str]
) -> None:
    """
    Swaps attributes between nodes with matching target id in both trees.
    """
    queue = deque([ltree, rtree])
    node1 = node2 = None
    while queue:
        lnode = queue.pop()
        if lnode is None:
            continue
        if lnode.node_id == target:
            if node1 is None:
                node1 = lnode
            elif node2 is None:
                node2 = lnode
                for att in attributes:
                    temp = getattr(node1, att)
                    setattr(node1, att, getattr(node2, att))
                    setattr(node2, att, temp)
        queue.extend([lnode.left, lnode.right])
