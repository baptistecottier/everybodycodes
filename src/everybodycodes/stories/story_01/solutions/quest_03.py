"""
Story: Echoes of Enigmatus
Quest: The Conical Snail Clock
"""

from math import lcm
from typing import Iterator


def preprocessing(
    puzzle_inputs: dict[int, str]
) -> list[set[tuple[int, int]]]:
    """
    Parse the raw input content into per-part structures.
    """
    parts_inputs: list[set[tuple[int, int]]] = []
    for note in puzzle_inputs.values():
        snails: set[tuple[int, int]] = set()
        for snail in note.splitlines():
            coords: list[str] = snail.split()
            x: int = int(coords[0][2:]) - 1
            y: int = int(coords[1][2:]) - 1
            snails.add((y, 1 + y + x))
        parts_inputs.append(snails)
    return parts_inputs


def solver(
    snails_groups: list[set[tuple[int, int]]]
) -> Iterator[int]:
    """
    Solve all puzzle parts for this quest.
    """
    snails = snails_groups[0]
    yield sum(
        (100 * ((y - 100) % mod + 1) + mod - ((y - 100) % mod))
        for y, mod in snails
    )
    for snails in snails_groups[1:]:
        yield chinese_remainder(snails)


def chinese_remainder(
    equations: set[tuple[int, int]]
) -> int:
    """
    Solves a system of congruences using the Chinese Remainder Theorem.
    """
    solution = 0
    product: int = lcm(*(modulo for _, modulo in equations))
    for remainder, modulo in equations:
        sub_product: int = product // modulo
        solution += remainder * pow(sub_product, -1, modulo) * sub_product
    return solution % product
