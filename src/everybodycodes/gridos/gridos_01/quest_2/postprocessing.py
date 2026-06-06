"""Postprocessing module for quest 2."""


def postprocessing(tapes: list[str]) -> int:
    """
    Count total '@' characters across all tapes.
    """
    return sum(tape.count("@") for tape in tapes)
