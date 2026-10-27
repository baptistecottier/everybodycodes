"""
Story: The Digital Atelier
Quest: The Recamán Drapery
"""

from typing import Iterator


def preprocessing(
        puzzle_inputs: dict[int, str]
) -> list[list[list[int]]]:
    """
    Parse the raw input content into per-part sequences of jumps.
    """
    inputs: list[int] = []
    for part in puzzle_inputs.values():
        sequences: list[list[int]] = []
        for sequence in part.splitlines():
            sequences.append(list(map(int, sequence.split(','))))
        inputs.append(sequences)
    return inputs


def solver(
        inputs: list[list[list[int]]]
) -> Iterator[int]:
    """
    Solve all puzzle parts for this quest.
    """
    for part, sequences in enumerate(inputs, 1):
        sum_point = 0
        for sequence in sequences:
            path = [0]
            point = 0
            for jump in sequence:
                tmp = find_next_available_point(
                    part, point, jump, path)
                if tmp == -1:
                    continue
                path.append(tmp)
                point = tmp
            sum_point += point
        yield sum_point


def find_next_available_point(
        part: int,
        point: int,
        distance: int,
        path: list[int]
) -> int:
    """
    Find the next point reachable by a jump of the given distance,
    respecting visited points and, for part 3, thread crossings.
    """
    pos = 1 - len(path) % 2
    connections = {(min(a, b), max(a, b))
                   for a, b in zip(path[pos::2], path[1 + pos::2])}

    def is_crossing(a, b):
        """
        Check whether the segment [a, b] crosses an existing connection.
        """
        start = min(a, b)
        end = a + b - start
        for low, up in connections:
            if start < low < end < up or low < start < up < end:
                return True
        return False

    visited = set(path)
    tmp = point - distance
    if ((tmp > 0)
            and tmp not in visited
            and (part != 3 or not is_crossing(point, tmp))):
        return tmp

    tmp = point + distance
    if part == 1:
        return tmp

    if part == 2:
        while tmp in visited:
            tmp += 1
        return tmp

    while tmp in visited or is_crossing(point, tmp):
        for s, e in connections:
            if tmp > e > point > s:
                return -1
        tmp += 1

    return tmp
