"""
Story: The Entertainment Hub
Quest: The Dice that Never Lie (Unless I Tell Them To)
"""

from collections import deque
from typing import Iterator, TypeAlias
from parse import Match, parse, Result  # type: ignore[import-untyped]

Dices: TypeAlias = list[tuple[int, list[int], int, int, int]]
RaceTrack: TypeAlias = list[list[int]]


def preprocessing(
    puzzle_inputs: dict[int, str]
) -> list[tuple[Dices, RaceTrack]]:
    """
    Parse the raw input content into per-part structures.
    """
    parts_inputs: list[tuple[Dices, RaceTrack]] = []

    for note in puzzle_inputs.values():
        extras: list[list[int]] = []
        dices: list[tuple[int, list[int], int, int, int]] = []
        for dice in note.splitlines():
            result: None | Result | Match = parse("{}: faces=[{}] seed={}",
                                                  dice)
            if not isinstance(result, Result):
                extras.append([int(d) for d in dice])
            else:
                dice_id, str_faces, seed = result
                faces: list[int] = list(map(int, str_faces.split(',')))
                dices.append((int(dice_id), faces, int(seed), int(seed), 0))
        parts_inputs.append((dices, extras[1:]))
    return parts_inputs


def solver(
    parts_input: list[tuple[Dices, RaceTrack]]
) -> Iterator[int | str]:
    """
    Solve all puzzle parts for this quest.
    """
    results = simulate_dices(parts_input[0][0])
    yield min(
        range(1_000),
        key=lambda roll: sum(sum(r[:roll]) for r in results) < 10_000)

    dices, racetrack = parts_input[1]
    results = simulate_dices(dices)
    for t in racetrack[0]:
        results = [r[r.index(int(t)) + 1:] for r in results]
    yield ','.join(str(n) for n in sorted(
        list(range(1, len(dices) + 1)),
        key=lambda r: -len(results[r - 1])))

    dices, racetrack = parts_input[2]
    results = simulate_dices(dices)
    all_visited: set[tuple[int, int]] = set()
    for result in results:
        all_visited.update(visited_tiles(racetrack, result))
    yield len(all_visited)


def simulate_dices(
    dices: list[tuple[int, list[int], int, int, int]]
) -> list[list[int]]:
    """
    Simulates rolling multiple dice with deterministic pseudo-random
    behavior based on pulse and spin mechanics.
    """
    n_roll = 0
    results: list[list[int]] = [[] for _ in range(len(dices))]

    while n_roll < len(dices) * 15_000:
        roll: int = 1 + n_roll // len(dices)
        dice_id, faces, seed, pulse, f = dices.pop(0)
        spin = roll * pulse
        f = (f + spin) % len(faces)
        results[n_roll % (1 + len(dices))].append(faces[f])
        pulse = (pulse + spin) % seed + 1 + roll + seed
        n_roll += 1
        dices.append((dice_id, faces, seed, pulse, f))

    return results


def visited_tiles(
    racetrack: RaceTrack,
    result: list[int]
) -> set[tuple[int, int]]:
    """
    Find all tiles that can be reached by following a sequence of
    characters matching the given result string.
    """
    h: int = len(racetrack)
    w: int = len(racetrack[0])
    neighbours: set[tuple[int, int]] = {
        (0, 1), (0, -1), (1, 0), (-1, 0), (0, 0)
        }

    visited: set[tuple[int, int, int]] = {
        (x, y, 1) for x in range(w) for y in range(h)
        if racetrack[y][x] == result[0]}
    queue: deque[tuple[int, int, int]] = deque(visited)

    while queue:
        x, y, idx = queue.popleft()
        r = result[idx]

        for dx, dy in neighbours:
            nx, ny = x + dx, y + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny, idx + 1) in visited:
                continue
            if racetrack[ny][nx] == r:
                queue.append((nx, ny, idx + 1))
                visited.add((nx, ny, idx + 1))

    return {(x, y) for (x, y, _) in visited}
