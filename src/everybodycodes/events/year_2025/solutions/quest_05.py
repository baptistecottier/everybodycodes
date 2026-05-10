"""
Event: The Song of Ducks and Dragons
Quest: Fishbone Order
"""

from collections import deque
from typing import Iterator


def preprocessing(puzzle_input: dict[int, str]) -> list[dict[int, list[int]]]:
    """
    Parse puzzle input and return sword data organized by part.
    """
    parts_inputs: list[dict[int, list[int]]] = []

    for notes in puzzle_input.values():
        swords: dict[int, list[int]] = {}
        for note in notes.splitlines():
            _sword_id, _numbers = note.split(":")
            sword_id = int(_sword_id)
            numbers: list[int] = [int(x) for x in _numbers.split(",")]
            swords[sword_id] = numbers
        parts_inputs.append(swords)

    return parts_inputs


def solver(records: list[dict[int, list[int]]]) -> Iterator[int]:
    """
    Solves the quest by building fishbone structures and calculating sword
    qualities.
    """
    for part, swords in enumerate(records, 1):
        qualities: list[tuple[int, list[int], int]] = []
        for sword_id, numbers in swords.items():
            fb: list[str] = build_fishbone(numbers)
            qualities.append(
                (
                    int("".join(fb[1::3])),  # Quality
                    [
                        int("".join(fb[i : i + 3]))  # Level numbers
                        for i in range(0, len(fb), 3)
                    ],
                    sword_id,
                )
            )  # Sword id
        qualities = sorted(qualities, reverse=True)

        match part:
            case 1:
                yield qualities[0][0]
            case 2:
                yield qualities[0][0] - qualities[-1][0]
            case 3:
                yield sum(
                    n * sword_id for n, (_, _, sword_id) in enumerate(qualities, 1)
                )
            case _:
                raise ValueError("Part does not exist!")


def build_fishbone(numbers: list[int]) -> list[str]:
    """
    Builds a fishbone structure from a list of numbers. In the worst case,
    only one side of the spine is filled, requiring len(numbers) / 2 levels.
    With 3 digits by layer this lead to 3/2 * len(numbers) list size. It also
    ensures fb[idx] does not raise an IndexError.
    """
    queue: deque[int] = deque(numbers)
    fb: list[int] = [0] * int(1.5 * len(numbers))
    fb[1] = queue.popleft()
    while queue:
        n = queue.popleft()
        idx = 1
        while True:
            if n < fb[idx] and fb[idx - 1] == 0:
                fb[idx - 1] = n
                break
            if n > fb[idx] and fb[idx + 1] == 0:
                fb[idx + 1] = n
                break
            if fb[idx + 3] == 0:
                fb[idx + 3] = n
                break
            idx += 3

    while fb[-1] == 0:  # Clean the sword tail
        fb.pop()

    return [str(n) if n != 0 else "" for n in fb]
