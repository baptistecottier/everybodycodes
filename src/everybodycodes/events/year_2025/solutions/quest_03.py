"""
Event: The Song of Ducks and Dragons
Quest: The Deepest Fit
"""

from typing import Iterator


def preprocessing(puzzle_input: dict[int, str]) -> list[list[int]]:
    """
    Parse the raw input content into per-part structures.
    """
    parts_inputs: list[list[int]] = []

    for note in puzzle_input.values():
        parts_inputs.append(list(map(int, note.split(","))))
    return parts_inputs


def solver(crate_sizes: list[list[int]]) -> Iterator[int]:
    """
    Solve all puzzle parts for this quest.
    """
    yield sum(set(crate_sizes[0]))
    yield sum(sorted(set(crate_sizes[1]))[:20])
    yield max(crate_sizes[2].count(n) for n in crate_sizes[2])
