"""
Event: Lord of the Wings
Quest: The Portalignment
"""

import re
from itertools import combinations
from collections import deque
from collections.abc import Iterator


def preprocessing(
        puzzle_inputs: dict[int, str]
) -> Iterator[tuple[int, dict[int, int]]]:
    """
    Parse each input into its number of portals and the shortcuts between
    portals, mapping each portal of a shortcut to the other one.
    """
    for data in puzzle_inputs.values():
        lines = data.split('\n\n')
        shortcuts = {}
        n_portals = int(lines.pop(0).split()[-1])
        for src, dst in re.findall(r'(\d+) (\d+)', lines.pop(0)):
            shortcuts[int(src) - 1] = int(dst) - 1
            shortcuts[int(dst) - 1] = int(src) - 1
        yield n_portals, shortcuts


def solver(rings: Iterator[tuple[int, dict[int, int]]]) -> Iterator[int]:
    """
    Yield, for each ring, a total computed from its number of portals that
    decreases by twice the fewest steps needed to go from one portal to
    another, for every pair of portals, moving around the ring or through a
    shortcut.
    """
    for i, (n_portals, shortcuts) in enumerate(rings):
        total = 0
        ngh = set(range(-(2 * i + 1), 2 * (i + 1)))
        n = ((n_portals - 1) // (2 * i + 1)) // 2
        total = (2 * i + 1) * (n + 1) ** 2 * n_portals

        for (p1, p2) in combinations(range(n_portals), 2):
            visited = {p1}
            queue = deque([(0, p1)])
            while queue:
                n, pos = queue.pop()
                if pos == p2:
                    break
                for dx in ngh:
                    nxt = (pos + dx) % n_portals
                    if nxt in visited:
                        continue
                    queue.appendleft((n + 1, nxt))
                if pos in shortcuts:
                    if shortcuts[pos] not in visited:
                        queue.appendleft((n + 1, shortcuts[pos]))

            total -= 2 * n
        yield total
