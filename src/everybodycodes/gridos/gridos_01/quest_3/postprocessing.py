"""Postprocessing module for quest 3."""


def postprocessing(tape: list[str]):
    """
    Remove empty lines and trim leading/trailing underscores from tape.
    """
    tape = [t for t in tape if set(list(t)) != {'_'}]

    while True:
        if all(t[0] == '_' for t in tape):
            tape = [t[1:] for t in tape]
        else:
            break

    while True:
        if all(t[-1] == '_' for t in tape):
            tape = [t[:-1] for t in tape]
        else:
            break

    return '\n'.join(tape).strip('_')
