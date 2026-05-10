"""
Event: The Kingdom of Algorithmia
Quest: The Tree of Titans
"""

from collections import defaultdict, deque
from typing import Iterator, TypeAlias

Tree: TypeAlias = defaultdict[str, set[str]]


def preprocessing(puzzle_input: dict[int, str]) -> list[Tree]:
    """
    Parse the raw input content into per-part structures.`
    """
    trees: list[Tree] = []
    for pi in puzzle_input.values():
        tree: Tree = defaultdict(set)
        for line in pi.splitlines():
            parent, children = line.split(":")
            tree[parent] = set(children.split(","))
        trees.append(tree)
    return trees


def solver(trees: list[Tree]) -> Iterator[str]:
    """
    Solve all puzzle parts for this quest.
    """
    yield "".join(most_powerful_fruit(trees[0]))
    for part in [2, 3]:
        yield "".join(f[0] for f in most_powerful_fruit(trees[part - 1]))


def most_powerful_fruit(tree: Tree) -> list[str]:
    """
    Return the unique path (as a list of node labels) starting from 'RR' that
    terminates at '@' while ignoring 'BUG' and 'ANT' children, or return an
    empty string if no such unique-length path exists.
    """
    branch_length: defaultdict[int, list[list[str]]] = defaultdict(list)
    start = "RR"
    queue: deque[list[str]] = deque([[start]])

    while queue:
        branch: list[str] = queue.popleft()
        fruit: str = branch[-1]
        if fruit == "@":
            branch_length[len(branch)].append(branch)
        for child in tree[fruit]:
            if child not in ["BUG", "ANT"]:
                queue.append(branch + [child])

    for _, branches in branch_length.items():
        if len(branches) == 1:
            return branches[0]

    return [""]
