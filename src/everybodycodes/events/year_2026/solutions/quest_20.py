"""
Event: Lord of the Wings
Quest: The Matchmatics
"""

import re
from typing import Iterator


def preprocessing(puzzle_inputs: dict[int, str]) -> Iterator[list[str]]:
    """
    Parse each input into its equations, one per line, spaces removed.
    """
    for notes in puzzle_inputs.values():
        yield notes.replace(' ', '').splitlines()


def solver(notes: Iterator[list[str]]) -> Iterator[str]:
    """
    Yield, for each notes, the total number of segments lit by its correct
    equations, written in base 10 for the first notes and in base 11 for the
    others. In the third notes, the equations that can be made correct by
    moving one segment count as well.
    """
    n_segments = {'0': 6, '1': 2, '2': 5, '3': 5, '4': 4,
                  '5': 5, '6': 6, '7': 3, '8': 7, '9': 6,
                  '+': 2, '-': 1, '=': 2, ' ': 0, 'A': 6
                  }

    for i, equations in enumerate(notes):
        base = 10 if i == 0 else 11
        total_seg = 0
        for eq in equations:
            if check(eq, base) or (i == 2 and fix(eq, base)):
                total_seg += sum(n_segments[c] for c in eq)
        yield number_to_base(total_seg, base)


def check(eq: str, base: int) -> bool:
    """
    Whether the equation, of the form a±b=c±d with its numbers written in
    the given base, is correct.
    """
    elems = re.search(r'([\d|A]+)(.[\d|A]+)=([\d|A]+)(.[\d|A]+)', eq)
    if not elems:
        return False
    items = [int(a, base) for a in elems.groups()]
    return items[0] + items[1] == items[2] + items[3]


def fix(eq: str, base: int) -> bool:
    """
    Whether the equation can be made correct by moving one segment, either
    inside a character (changing it into another one with as many segments),
    or from a character to another one.
    """
    alternatives = {'0': ['6', '9', 'A'], '2': ['3'], '3': ['5', '2'],
                    '5': ['3'], '6': ['0', '9', 'A'], '9': ['0', '6', 'A'],
                    'A': ['0', '6', '9']
                    }
    add_segment = {'0': ['8'], '1': ['7'], '3': ['9'], '5': ['6', '9'],
                   '6': ['8'], '9': ['8'], 'A': ['8'], '-': ['+'],
                   }
    remove_segment = {'6': ['5'], '7': ['1'], '8': ['6', '9', '0', 'A'],
                      '9': ['5', '3'], '+': ['-']
                      }

    # Check for substitutions
    for i, c in enumerate(eq):
        for alt in alternatives.get(c, []):
            neq = eq[:i] + alt + eq[i+1:]
            if check(neq, base):
                return True

    # Check for segment moving
    for i, c in enumerate(eq):
        for added in add_segment.get(c, []):
            neq = eq[:i] + added + eq[i+1:]
            for j, c2 in enumerate(eq):
                if i == j:
                    continue
                for removed in remove_segment.get(c2, []):
                    neq2 = neq[:j] + removed + neq[j+1:]
                    if check(neq2, base):
                        return True
    return False


def number_to_base(n: int, b: int) -> str:
    """
    Write n in base b, with the letters A to H for the digits above nine.
    """
    char = "0123456789ABCDEFGH"
    if n == 0:
        return '0'
    digits: list[int] = []
    while n:
        digits.append(int(n % b))
        n //= b
    return ''.join(char[d] for d in digits[::-1])
