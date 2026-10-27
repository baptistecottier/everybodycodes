from math import lcm

def preprocessing(
        puzzle_input: dict[int, str]
):
    pattern_plans = []
    for data in puzzle_input.values():
        if not data:
            continue
        plan = []
        lines = data.splitlines()
        plan.append(int(lines[0].split('=')[1]))  # Width
        plan.append(int(lines[1].split('=')[1]))  # Height
        plan.append(list(map(int, lines[2].split('=')[1])))  # Horizontal offsets
        plan.append(list(map(int, lines[3].split('=')[1])))  # Vertical offsets
        pattern_plans.append(plan)
    return pattern_plans


def solver(pattern_plans):
    yield sum(count_isolated_tiles(pattern_plans[0]))
    yield max(count_isolated_tiles(pattern_plans[1]))
    yield max(count_isolated_tiles(pattern_plans[2]))


def count_isolated_tiles(pattern_plan):
    w, h, ho, vo = pattern_plan
    hl = len(ho)
    vl = len(vo)

    period_x = lcm(2, vl)
    period_y = lcm(2, hl)

    vz = [0] * period_x
    zone = 0
    for x in range(period_x):
        vz[x] = zone
        if vo[(x + 1) % vl] == 0:
            zone ^= 1

    hz = [[0] * period_y, [0] * period_y]
    for b in (0, 1):
        zone = 0
        for y in range(period_y):
            hz[b][y] = zone
            if ho[(y + 1) % hl] == b:
                zone ^= 1

    def repeats(total, period, offset):
        return max(0, (total - offset - 1) // period + 1)

    score_by_zone = [0, 0]
    for y in range(period_y):
        for x in range(period_x):
            if ((x % 2 == ho[y % hl]) and
                    (y % 2 == vo[x % vl]) and
                    (vo[x % vl] == vo[(x + 1) % vl]) and
                    (ho[y % hl] == ho[(y + 1) % hl])):
                reps = repeats(w, period_x, x) * repeats(h, period_y, y)
                if reps:
                    score_by_zone[vz[x] ^ hz[x % 2][y]] += reps
    return score_by_zone