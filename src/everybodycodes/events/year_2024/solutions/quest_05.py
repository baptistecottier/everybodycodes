"""
Event: The Kingdom of Algorithmia
Quest: Pseudo-Random Clap Dance
"""

from collections import defaultdict
from typing import Iterator, TypeAlias

Dancers: TypeAlias = list[list[int]]


def preprocessing(puzzle_input: dict[int, str]) -> list[Dancers]:
    """
    Parse the raw input content into per-part structures.
    """
    lines: list[Dancers] = []
    for note in puzzle_input.values():
        chests: list[int] = list(map(int, note.split()))
        lines.append([chests[i::4] for i in range(4)])
    return lines


def solver(rounds_dancers: list[Dancers]) -> Iterator[int]:
    """
    Yield solutions for each puzzle part by parsing the provided input
    content and invoking play with the corresponding parameters.
    """
    for dancers, kwargs in zip(
        rounds_dancers, ({"max_rounds": 10}, {"n_shouts": 2024}, {})
    ):
        yield play(dancers, **kwargs)


def play(dancers: Dancers, max_rounds: int = 0, n_shouts: int = 0) -> int:
    """
    Simulate a four-column dancer rotation, tracking seen states and shout
    frequencies, and return either the most frequent shout upon cycle
    detection, the shout at a specified round, or the product of a shout and
    its round when it reaches n_shouts depending on max_rounds and n_shouts.
    """
    positions: set[str] = set()
    shouts: defaultdict[int, int] = defaultdict(int)
    rnd: int = 0

    while True:
        x_idx: int = (rnd + 1) % 4
        clmn_size: int = len(dancers[x_idx])

        dancer = dancers[rnd % 4].pop(0)
        y_idx = (dancer - 1) % (2 * clmn_size)
        if y_idx > clmn_size:
            y_idx = 2 * clmn_size - y_idx

        dancers[x_idx].insert(y_idx, dancer)
        shout = int("".join(str(dancers[i][0]) for i in range(4)))

        if max_rounds == n_shouts == 0:
            state: str = f"{''.join(str(c) for clmn in dancers for c in clmn)}"
            if state in positions:
                return max(shouts.keys())
            positions.add(state)

        rnd += 1
        if rnd == max_rounds:
            return shout

        shouts[shout] += 1
        if shouts[shout] == n_shouts:
            return shout * rnd
