"""Postprocessing module for quest 4."""


def postprocessing(tape: list[str]):
    """
    Remove empty lines and trim leading/trailing underscores from tape.
    """
    return [t.strip('_') for t in tape if set(list(t)) != {'_'}]
