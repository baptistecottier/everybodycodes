"""
Event: The Song of Ducks and Dragons
Quest: From Complex to Clarity
"""

from dataclasses import dataclass
from itertools import product
from typing import Iterator


@dataclass
class Complex:
    """
    Class representing complex numbers
    """

    real: int
    img: int

    def update_and_verify(self, cycles: int, divisor: int) -> bool:
        """
        Update self value for verification and checks if it remains between
        bounds.
        """
        r = Complex(0, 0)
        for _ in range(cycles):
            temp: int = int((r.real**2 - r.img**2) / divisor) + self.real
            r.img = int(r.real * r.img * 2 / divisor) + self.img
            r.real = temp
            if not (
                -1_000_000 <= r.real <= 1_000_000 and -1_000_000 <= r.img <= 1_000_000
            ):
                return False
        self.real = r.real
        self.img = r.img
        return True

    def __str__(self) -> str:
        """
        Format the complex number with the bracketed puzzle representation.
        """
        return f"[{self.real},{self.img}]"


def preprocessing(puzzle_input: dict[int, str]):
    """
    Parse and returns complex numbers provided as part inputs.
    """
    parts_inputs: list[Complex] = []
    for note in puzzle_input.values():
        leftb: int = note.index("[")
        rightb: int = note.index("]")
        comma: int = note.index(",")
        r = int(note[leftb + 1 : comma])
        i = int(note[comma + 1 : rightb])
        parts_inputs.append(Complex(r, i))
    return parts_inputs


def solver(numbers: list[Complex]) -> Iterator[Complex | int]:
    """
    Checks verification process with the first input then determine the number
    of points to engrave according to two different levels of precision.
    """
    cplx = numbers[0]
    cplx.update_and_verify(3, 10)
    yield cplx

    for step, cplx in zip((10, 1), numbers[1:]):
        engraved = 0
        for real, img in product(
            range(cplx.real, cplx.real + 1_001, step),
            range(cplx.img, cplx.img + 1_001, step),
        ):
            engraved += Complex(real, img).update_and_verify(100, 100_000)
        yield engraved
