"""
Event: The Song of Ducks and Dragons
Quest: Whispers in the Shell
"""

from typing import Iterator


def preprocessing(
    puzzle_input: dict[int, str]
) -> list[tuple[list[str], list[int]]]:
    """
    Parse the raw input content into per-part structures.
    """
    parts_inputs: list[tuple[list[str], list[int]]] = []
    for note in puzzle_input.values():
        _names, _moves = note.split("\n\n")
        names: list[str] = _names.split(",")
        moves: list[int] = [
            int(n)
            for n in _moves.replace("R", "").replace("L", "-").split(",")
        ]
        parts_inputs.append((names, moves))
    return parts_inputs


def solver(
    sections: list[tuple[list[str], list[int]]]
) -> Iterator[str]:
    """
    Solve all puzzle parts for this quest.
    """
    for part, (names, moves) in enumerate(sections, 1):
        idx = 0
        for n in moves:
            if part != 3:
                idx += n
                if part == 1:
                    idx = min(len(names) - 1, max(idx, 0))
                if part == 2:
                    idx %= len(names)
            else:
                n %= len(names)
                names[0], names[n] = names[n], names[0]
        yield names[idx]
