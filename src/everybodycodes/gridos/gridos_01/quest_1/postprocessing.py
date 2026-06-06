"""Postprocessing module for quest 1."""


def postprocessing(tapes: list[str]) -> int:
    """
    Ensures all non-empty values are 'P' and count them.
    """
    cnt = 0
    for tape in tapes:
        p_cnt = tape.count('P')
        if len(tape.replace('_', '')) == p_cnt:
            cnt += p_cnt
    return cnt
