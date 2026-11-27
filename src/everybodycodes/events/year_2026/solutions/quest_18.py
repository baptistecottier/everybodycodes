"""
Event: Lord of the Wings
Quest: The Keyometry
"""

import re
from collections.abc import Iterator


def preprocessing(
        puzzle_inputs: dict[int, str]
) -> list[list[tuple[int, int, int]]]:
    """
    Parse each input into the sorted list of its measurements, each made of
    an x coordinate, a y coordinate and an optional count (1 if missing).
    """
    return [
        sorted(
            (int(a), int(b), int(c) if c else 1)
            for a, b, c in re.findall(
                 r'x=(\d+) y=(\d+)(?:\D*)(\d*)(?:\n|$)', notes
            )
        )
        for notes in puzzle_inputs.values()
    ]


def solver(
        list_of_measurements: list[list[tuple[int, int, int]]]
) -> Iterator[int]:
    """
    Yield, for each input, the number of cells below the steps which rise from
    the left and from the right up to the highest measurements, plus the cells
    at the maximal height between those two measurements.
    """
    for measurements in list_of_measurements:
        units = 0
        max_y = max(y for _, y, _ in measurements)
        max_x = measurements[-1][0] + measurements[-1][2] + 2
        mirror = [(max_x - x - w, y) for x, y, w in measurements[::-1]]
        measurements = [(x, y) for (x, y, _) in measurements]
        at_top = max_x

        for data in (measurements, mirror):
            i = 0
            lx, h = data[i]
            while h < max_y:
                i += 1
                x, y = data[i]
                if y < h:
                    continue
                units += (x - lx) * h
                h, lx = y, x
            at_top -= lx
        units += at_top * max_y
        yield units
