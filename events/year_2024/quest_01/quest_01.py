
"""
Event: The Kingdom of Algorithmia
Quest: The Battle for the Farmlands
"""

from collections.abc import Iterator
from collections import defaultdict


def preprocessing(puzzle_input: dict[int, str]) -> list[str]:
    """
    Parse the per-part input dictionary into stripped part strings.
    """
    return list(puzzle_input.values())


def solver(creatures: list[str]) -> Iterator[int]:
    """
    Yield the solution for each part by parsing dict input and counting
    potions.
    """
    for fight in enumerate(creatures, 1):
        yield count_potions(*fight)


def count_potions(level: int, creatures: str) -> int:
    """
    Calculate the total potions needed to defeat groups of creatures.

    Creatures are grouped by the given level size, and each creature type
    has a base potion cost. Additionally, non-'x' creatures in a group
    contribute bonus potions: (p * (p - 1)) where p is the count of
    non-'x' creatures.

    Args:
        creatures (str): A string of creature type characters (A, B, C, D, x).
        level (int): The group size for partitioning creatures.

    Returns:
        int: Total potions required.

    Creature costs:
        - 'A': 0 base potions
        - 'B': 1 base potion
        - 'C': 3 base potions
        - 'D': 5 base potions
        - 'x': 0 base potions

    Example:
        >>> count_potions("ABCX", 1)
        9
        >>> count_potions("ABCX", 4)
        10
    """
    cost = defaultdict(lambda: 0)
    cost.update({'B': 1, 'C': 3, 'D': 5})
    potions = 0

    for i in range(0, len(creatures), level):
        group = creatures[i: i + level]
        potions += sum(cost[g] for g in group)
        score = level - group.count('x')
        potions += score * (score - 1)

    return potions
