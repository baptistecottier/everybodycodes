"""Postprocessing module for quest 1 part 1."""


def postprocessing(tapes: list[str]) -> int:
    """
    Count total 'P' characters across all tapes.
    """
    return sum(tape.count("P") for tape in tapes)
