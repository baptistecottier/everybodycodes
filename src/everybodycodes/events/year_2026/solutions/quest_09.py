"""
Event: Lord of the Wings
Quest: The Sulphurprise
"""

import re
from collections import defaultdict
from typing import Callable, Iterator


def preprocessing(puzzle_inputs: dict[int, str]) -> list[list[list[int]]]:
    """
    Parse each input into its list of [growth, limit] pairs.
    """
    return [
        [list(map(int, result))
         for result in re.findall(
             r'id=\d+, growth=(\d+), limit=(\d+)',
             notes)]
        for notes in puzzle_inputs.values()
    ]


def solver(
        notes: list[list[list[int]]]
) -> Iterator[int]:
    """
    Yield the total number of seconds needed by the pairs of the first notes,
    counting the nodes plus the summed ages of the elements, then by those of
    the second notes, counting the nodes plus one.
    """
    yield simulate(notes[0], lambda x: sum(k * v for k, v in x.items()))
    yield simulate(notes[1], lambda x: 1)


def simulate(
        notes: list[list[int]], f_cond: Callable[[dict[int, int]], int]
) -> int:
    """
    Return the total number of seconds needed by each [growth, limit] pair of
    notes to reach its limit. Starting from one element of age 0, every
    element ages by one each second; those reaching growth become nodes,
    restart at age 1 and add twice their number at age growth // 2. A pair is
    done once the nodes plus f_cond of the elements, by age, reach the limit.
    """
    seconds = 0
    for growth, limit in notes:
        t = 0
        nodes = 0
        elems: dict[int, int] = defaultdict(int)
        elems[0] = 1
        while nodes + f_cond(elems) < limit:
            elems = {k + 1: v for k, v in elems.items()}
            if growth in elems:
                nodes += elems[growth]
                elems[1] = elems[growth]
                elems[growth // 2] = (
                    elems.get(growth // 2, 0)
                    + 2 * elems[growth]
                )
                del elems[growth]
            t += 1
        seconds += t
    return seconds
