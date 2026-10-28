"""
Event: Lord of the Wings
Quest: The Axeperiment
"""

from collections import defaultdict
from typing import Iterator

type Comparison = tuple[int, int]


def preprocessing(
        puzzle_input: dict[int, str]
) -> list[list[list[Comparison]]]:
    """
    Parse each line of the input into a group of (low, high) comparisons.
    """
    puzzle_inputs: list[list[list[Comparison]]] = []
    for pi in puzzle_input.values():
        groups: list[list[Comparison]] = []
        for group in pi.splitlines():
            groups.append(
                [get_low_and_high(calc) for calc in group.split(' ')])
        puzzle_inputs.append(groups)
    return puzzle_inputs


def solver(notes: list[list[list[Comparison]]]) -> Iterator[int]:
    """
    For each note, order the alloys of every group from the comparisons
    and yield the sum of the orderings read as integers.
    """
    for note in notes:
        cs = 0
        for comp in note:
            order: defaultdict[int, set[int]] = defaultdict(set)
            for a, b in comp:
                order[a].add(b)
                if b not in order:
                    order[b] = set()
            n = max(order.keys())
            target = n * (n - 1) // 2
            while sum(len(alloy) for alloy in order.values()) < target:
                for alloy in list(order.values()):
                    for lower_alloy in alloy.copy():
                        alloy.update(order[lower_alloy])

            sorted_alloys = sorted(order.items(), key=lambda x: len(x[1]))
            cs += int("".join(str(a) for a, _ in sorted_alloys))
        yield cs


def get_low_and_high(calc: str) -> Comparison:
    """
    Return the (low, high) pair of a comparison such as "3<5" or "5>3".
    """
    if '>' in calc:
        return (int(calc[2]), int(calc[0]))
    return (int(calc[0]), int(calc[2]))
