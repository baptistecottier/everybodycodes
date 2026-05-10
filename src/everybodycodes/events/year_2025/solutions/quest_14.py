"""
Event: The Song of Ducks and Dragons
Quest: The Game of Light
"""

from itertools import product
from typing import Iterator


def preprocessing(
    puzzle_inputs: dict[int, str],
) -> list[tuple[set[tuple[int, int]], tuple[int, int]]]:
    """
    Parse the raw input content into per-part structures.
    """
    parts_inputs: list[tuple[set[tuple[int, int]], tuple[int, int]]] = []
    for puzzle_input in puzzle_inputs.values():
        tiles: set[tuple[int, int]] = set()
        x = y = 0
        for y, line in enumerate(puzzle_input.splitlines()):
            for x, c in enumerate(line):
                if c == "#":
                    tiles.add((x, y))
        parts_inputs.append((tiles, (x + 1, y + 1)))
    return parts_inputs


def solver(
    floor_sections: list[tuple[set[tuple[int, int]], tuple[int, int]]],
) -> Iterator[int]:
    """
    Solve all puzzle parts for this quest.
    """
    yield count_tiles(*floor_sections[0], rounds=10, center=set())
    yield count_tiles(*floor_sections[1], rounds=2025, center=set())
    yield count_tiles(set(), (34, 34), 1000000000, *floor_sections[2])


def count_tiles(
    tiles: set[tuple[int, int]],
    floor_size: tuple[int, int],
    rounds: int,
    center: set[tuple[int, int]],
    center_size: tuple[int, int] = (0, 0),
) -> int:
    """
    Counts active tiles over multiple rounds, detecting cycles to handle large
    round numbers efficiently.
    """
    seen: list[set[tuple[int, int]]] = []
    centers: list[tuple[int, int]] = []
    w, h = floor_size
    cw, ch = center_size
    sx, sy = (w - cw) // 2, (h - ch) // 2

    for r in range(rounds):
        seen.append(tiles)
        tiles = update_tiles(tiles, w, h)

        if all(
            ((sx + x, sy + y) in tiles) == ((x, y) in center)
            for (x, y) in product(range(cw), range(ch))
        ):
            centers.append((r, len(tiles)))

        if tiles in seen:
            activated = sum(ell for _, ell in centers) * (rounds // r)
            activated += sum(ell for n, ell in centers if n <= rounds % r)
            return activated

    return sum(ell for _, ell in centers)


def update_tiles(tiles: set[tuple[int, int]], w: int, h: int) -> set[tuple[int, int]]:
    """
    Updates tiles based on a score calculated from neighboring tile positions,
    keeping tiles where the parity of neighbors matches the current tile state.
    """
    updated_tiles: set[tuple[int, int]] = set()

    for x, y in product(range(w), range(h)):
        score: int = sum(
            (x + dx, y + dy) in tiles for dx, dy in product((-1, 1), repeat=2)
        )
        if score % 2 == ((x, y) in tiles):
            updated_tiles.add((x, y))

    return updated_tiles
