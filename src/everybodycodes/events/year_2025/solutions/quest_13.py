"""
Event: The Song of Ducks and Dragons
Quest: Unlocking the Mountain
"""

from typing import Iterator


def preprocessing(puzzle_inputs: dict[int, str]) -> list[list[int]]:
    """
    Parse the raw input content into per-part structures.
    """
    parts_inputs: list[list[int]] = []

    for puzzle_input in puzzle_inputs.values():
        lines: list[str] = [
            "-".join(line for _ in range(2 - line.count("-")))
            for line in puzzle_input.splitlines()
        ]
        values: list[int] = [1]
        for delta in (1, -1):
            for line in lines[(delta == -1) :: 2][::delta]:
                s, e = [int(x) for x in line.split("-")][::delta]
                values += list(range(s, e + delta, delta))
        parts_inputs.append(values)
    return parts_inputs


def solver(numbers: list[list[int]]) -> Iterator[int]:
    """
    Solve all puzzle parts for this quest.
    """
    for part, wheel in enumerate(numbers, 1):
        yield wheel[sum(2025 * 10_000**i for i in range(part)) % len(wheel)]
