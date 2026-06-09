"""
Event: The Kingdom of Algorithmia
Quest: Cat Grin of Fortune
"""

from math import lcm
from collections import Counter
from typing import Iterator


def preprocessing(
    puzzle_input: dict[int, str]
) -> list[list[list[str]]]:
    """
    Parse the raw input content into per-part structures.
    """
    parts_input: list[list[list[str]]] = []
    for note in puzzle_input.values():
        blocs: list[str] = note.split("\n\n")
        str_pulls = blocs[0]
        str_wheels = blocs[1]
        symbols: list[str] = str_wheels.splitlines()
        wheels: list[list[str]] = []
        for w, n in enumerate(map(int, str_pulls.split(","))):
            wheel: list[str] = [
                w
                for w in [symbol[4 * w: 4 * w + 3] for symbol in symbols]
                if w != "" and " " not in w
            ]
            idxs: list[int] = [0]
            idx: int = n % len(wheel)
            while idx not in idxs:
                idxs.append(idx)
                idx = (idx + n) % len(wheel)
            wheel = [wheel[i] for i in idxs]
            wheels.append(wheel)
        parts_input.append(wheels)
    return parts_input


def solver(
    wheels: str
) -> Iterator[str | int]:
    """
    Solves the quest by calculating wheel sequences and counting byte coins
    for the given input.
    """
    yield " ".join(w[100 % len(w)] for w in wheels[0])

    n: int = lcm(*(len(w) for w in wheels[1]))
    pulls = 202_420_242_024
    byte_coins: list[int] = [0]
    for i in range(1, n + 1):
        sequence: str = " ".join(w[i % len(w)] for w in wheels[1])
        byte_coins.append(count_byte_coins(sequence[::2]))
    yield (pulls // n) * sum(byte_coins) + sum(byte_coins[: 1 + pulls % n])


def count_byte_coins(
    sequence: str
) -> int:
    """
    Count the number of byte coins by summing the excess occurrences beyond 2
    for each element in the sequence.
    """
    return sum(max(0, v - 2) for v in Counter(sequence).values())
