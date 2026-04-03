"""
Event: The Kingdom of Algorithmia
Quest 9: Sparkling Bugs
"""

from typing import Iterator


def preprocessing(
    puzzle_input: dict[int, str]
) -> list[list[int]]:
    """
    Parse the raw input content into per-part structures.
    """
    return [list(map(int, pi.splitlines())) for pi in puzzle_input.values()]


def solver(
    sparkballs: list[list[int]]
) -> Iterator[int]:
    """
    Solve all puzzle parts for this quest.
    """
    dots: list[int] = [
        1,   3,  5, 10, 15, 16, 20,  24,   25,
        30, 37, 38, 49, 50, 74, 75, 100, 101
        ]
    for part, sbs in enumerate(sparkballs):
        yield get_min_beetles(sbs, dots[:[4, 10, 18][part]])


def get_min_beetles(
    sparkballs: list[int],
    dots: list[int]
) -> int:
    """
    Calculate the minimum number of beetles needed to collect exactly
    sparkballs using dynamic programming.
    """
    max_sb = max(sparkballs)

    beetles = [float('inf')] * (max_sb + 1)
    beetles[0] = 0

    for i in range(1, max_sb + 1):
        beetles[i] = min(1 + beetles[i - dot] for dot in dots if i >= dot)

    total_beetles = 0
    for sb in sparkballs:

        if sb > 50_000:
            min_beetles = sb
            for delta in range(0, 51):
                lhs = sb // 2 - delta + sb % 2
                rhs = sb - lhs
                min_beetles = min(
                    beetles[lhs] + beetles[rhs], min_beetles)
            total_beetles += min_beetles

        else:
            total_beetles += beetles[sb]

    return int(total_beetles)
