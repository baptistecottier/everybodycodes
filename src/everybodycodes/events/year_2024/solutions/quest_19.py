"""
Event: The Kingdom of Algorithmia
Quest: Encrypted Duck
"""

from itertools import product
from typing import Iterator


def preprocessing(puzzle_input: dict[int, str]) -> list[tuple[str, list[list[str]]]]:
    """
    Parse the raw input content into per-part structures.
    """
    parts_inputs: list[tuple[str, list[list[str]]]] = []
    for note in puzzle_input.values():
        ops, _cipher = note.split("\n\n")
        cipher: list[list[str]] = [list(line) for line in _cipher.splitlines()]
        parts_inputs.append((ops, cipher))
    return parts_inputs


def solver(messages: list[tuple[str, list[list[str]]]]) -> Iterator[str]:
    """
    Solve all puzzle parts for this quest.
    """
    for n, (ops, cipher) in enumerate(messages[:2]):
        h: int = len(cipher)
        w: int = len(cipher[0])
        rep: int = [1, 100, 1048576000][n]
        for _ in range(rep):
            idx = 0
            for y, x in product(range(1, h - 1), range(1, w - 1)):
                if ops[idx] == "R":
                    cipher = rotate_right(cipher, x, y)
                else:
                    cipher = rotate_left(cipher, x, y)
                idx = (idx + 1) % len(ops)
        plain: str = "".join(c for line in cipher for c in line)
        yield plain[plain.index(">") + 1 : plain.index("<")]


def rotate_left(cipher: list[list[str]], x: int, y: int) -> list[list[str]]:
    """
    Rotate the eight cells around one center one step counterclockwise.
    """
    temp = cipher[y - 1][x - 1]
    for nx, ny in (
        (x - 1, y),
        (x - 1, y + 1),
        (x, y + 1),
        (x + 1, y + 1),
        (x + 1, y),
        (x + 1, y - 1),
        (x, y - 1),
        (x - 1, y - 1),
    ):
        cipher[ny][nx], temp = temp, cipher[ny][nx]
    return cipher


def rotate_right(cipher: list[list[str]], x: int, y: int) -> list[list[str]]:
    """
    Rotate the eight cells around one center one step clockwise.
    """
    temp = cipher[y - 1][x - 1]
    for nx, ny in (
        (x, y - 1),
        (x + 1, y - 1),
        (x + 1, y),
        (x + 1, y + 1),
        (x, y + 1),
        (x - 1, y + 1),
        (x - 1, y),
        (x - 1, y - 1),
    ):
        cipher[ny][nx], temp = temp, cipher[ny][nx]
    return cipher
