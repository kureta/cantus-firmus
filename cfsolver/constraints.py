from collections import Counter
from itertools import product

from music21 import scale
from music21.interval import Interval
from music21.lily.translate import LilypondConverter
from music21.pitch import Pitch

from cfsolver import cf_above
from cfsolver import cf_below
from cfsolver.cf_any import *


def get_harmonies(register, cantus_firmus, is_wide=True, is_cf_above=False):
    # 1-note filters
    # Allowed vertical intervals
    if is_cf_above:
        c = cf_above
        first_intervals = c.perfect_octaves
    else:
        c = cf_below
        first_intervals = c.perfect_intervals

    if is_wide:
        allowed_intervals = c.vertical_intervals + c.optional_verticals
    else:
        allowed_intervals = c.vertical_intervals

    if Interval(cantus_firmus[-2], cantus_firmus[-1]).direction == 1:
        penultimate_intervals = c.tenorizans
    else:
        penultimate_intervals = c.cantizans
    first = [n for n in register if Interval(cantus_firmus[0], n) in first_intervals]
    penultimate = [n for n in register if Interval(cantus_firmus[-1], n) in penultimate_intervals]
    last = [n for n in register if Interval(cantus_firmus[-1], n) in c.perfect_octaves]
    others = [[n for n in register if Interval(cf, n) in allowed_intervals] for cf in cantus_firmus[1:-2]]
    singles = [first] + others + [penultimate] + [last]

    return singles


def is_melodic(pair):
    return Interval(*pair).name in melodic_intervals


def is_repeating(pair):
    return pair[0] == pair[1]


def is_parallel_5_or_8(pair, cf, is_cf_above=False):
    if is_cf_above:
        c = cf_above
    else:
        c = cf_below

    interval1 = Interval(cf[0], pair[0])
    interval2 = Interval(cf[1], pair[1])
    if (interval1 in c.perfect_fifths) and (interval2 in c.perfect_fifths):
        return True
    if (interval1 in c.perfect_octaves) and (interval2 in c.perfect_octaves):
        return True
    return False


def is_opposite_motion_to_perfect(pair, cf, is_cf_above=False):
    if is_cf_above:
        c = cf_above
    else:
        c = cf_below
    h_interval2 = Interval(cf[1], pair[1])
    m_interval1 = Interval(cf[0], cf[1])
    m_interval2 = Interval(pair[0], pair[1])

    if h_interval2 in c.perfect_intervals:
        return m_interval1.direction != m_interval2.direction
    return True


def is_exchanging_voices(pair, cf):
    # TODO: maybe with `simpleName` instead of `name`
    if pair[0].name == cf[1].name and pair[1].name == cf[0].name:
        return True
    return False


def is_valid_pair(pair, cantus_firmus, is_cf_above=False):
    return (
            is_melodic(pair)
            and not is_repeating(pair)
            and not is_parallel_5_or_8(pair, cantus_firmus, is_cf_above=is_cf_above)
            and is_opposite_motion_to_perfect(pair, cantus_firmus, is_cf_above=is_cf_above)
            and not is_exchanging_voices(pair, cantus_firmus)
    )


def get_pairs(harmonies, cantus_firmus, is_cf_above=False):
    pairs = []
    for idx, (left, right) in enumerate(zip(harmonies[:-1], harmonies[1:])):
        steps = []
        for pair in product(left, right):
            if is_valid_pair(pair, cantus_firmus[idx:idx + 2], is_cf_above=is_cf_above):
                steps.append(pair)
        pairs.append(steps)

    return pairs


def is_continuation(tuplet_pair):
    first, second = tuplet_pair
    return first[1:] == second[:-1]


def is_arpeggio(triplet):
    i1 = Interval(triplet[0], triplet[1]).directedSimpleName
    i2 = Interval(triplet[1], triplet[2]).directedSimpleName

    return [i1, i2] in arpeggio_intervals


def is_repeating_intervals(triplet, cf):
    i1 = Interval(triplet[0], cf[0]).simpleName
    i2 = Interval(triplet[1], cf[1]).simpleName
    i3 = Interval(triplet[2], cf[2]).simpleName

    return i1[-1] == i2[-1] == i3[-1]


def is_closing_leap(triplet):
    i1 = Interval(triplet[0], triplet[1]).chromatic.semitones
    i2 = Interval(triplet[1], triplet[2]).chromatic.semitones

    sign = i1 // abs(i1)
    if abs(i1) >= 5 and (i2 not in [-sign * 1, -sign * 2]):
        return False
    return True


def is_valid_triplet(triplet, cantus_firmus):
    return (
            not is_arpeggio(triplet)
            and not is_repeating_intervals(triplet, cantus_firmus)
            and is_closing_leap(triplet)
    )


def generate_next_tuplet(previous_tuplet, cantus_firmus, predicate):
    next_tuplets = []
    for idx, (left, right) in enumerate(zip(previous_tuplet[:-1], previous_tuplet[1:])):
        steps = []
        for pair in product(left, right):
            if is_continuation(pair):
                next_tuplet = pair[0] + pair[1][-1:]
                if predicate(next_tuplet, cantus_firmus[idx:idx + len(next_tuplet)]):
                    steps.append(list(next_tuplet))
        next_tuplets.append(steps)

    return next_tuplets


def is_jumpy(quadruplet):
    return all([abs(Interval(p1, p2).chromatic.semitones) > 3 for p1, p2 in zip(quadruplet[:-1], quadruplet[1:])])


def is_valid_quadruplet(quadruplet, _):
    return not is_jumpy(quadruplet)


def preferred_vertical_intervals(tuplet, cf, more, less):
    good = []
    bad = []
    for t, c in zip(tuplet, cf):
        intv = int(Interval(c, t).simpleName[-1])
        if intv in more:
            good.append(intv)
        elif intv in less:
            bad.append(intv)

    return len(good) > len(bad)


def has_more_imperfect_intervals(tuplet, cf):
    return preferred_vertical_intervals(tuplet, cf, (3, 6), (1, 5, 8))


def has_more_5ths_than_8ths(tuplet, cf):
    return preferred_vertical_intervals(tuplet, cf, (5,), (1, 8))


def has_more_steps_than_leaps(tuplet):
    steps = []
    leaps = []
    for first, second in zip(tuplet[:-1], tuplet[1:]):
        intv = int(Interval(first, second).name[-1])
        if intv <= 2:
            steps.append(intv)
        else:
            leaps.append(intv)
    return len(steps) > len(leaps)


def has_more_contrary_motion_than_not(tuplet, cf):
    contrary = []
    other = []
    for p1, p2, c1, c2 in zip(tuplet[:-1], tuplet[1:], cf[:-1], cf[1:]):
        ip = Interval(p1, p2)
        ic = Interval(c1, c2)

        if ip.direction != ic.direction:
            contrary.append(1)
        else:
            other.append(1)
    return len(contrary) > len(other)


def is_varied(tuplet):
    counts = Counter(tuplet)
    if all(val <= 3 for val in counts.values()) and (list(counts.values()).count(3) < 2):
        for idx in range(len(tuplet) - 4):
            if tuplet[idx] == tuplet[idx + 2] == tuplet[idx + 4]:
                return False
        for idx in range(len(tuplet) - 3):
            if (tuplet[idx] == tuplet[idx + 2]) and (tuplet[idx + 1] == tuplet[idx + 3]):
                return False
        return True
    return False


def is_good(tuplets, cf):
    return (
            has_more_imperfect_intervals(tuplets, cf)
            and has_more_steps_than_leaps(tuplets)
            and is_varied(tuplets)
            and has_more_contrary_motion_than_not(tuplets, cf)
    )


def do_it(cantus_firmus, register, is_wide=True, is_cf_above=False):
    harmonies = get_harmonies(register, cantus_firmus, is_wide=is_wide, is_cf_above=is_cf_above)
    pairs = get_pairs(harmonies, cantus_firmus, is_cf_above=is_cf_above)
    triplets = generate_next_tuplet(pairs, cantus_firmus, is_valid_triplet)
    quadruplets = generate_next_tuplet(triplets, cantus_firmus, is_valid_quadruplet)
    results = quadruplets
    while len(results) > 1:
        results = generate_next_tuplet(results, cantus_firmus, lambda x, y: True)
    results = [r for r in results[0] if is_good(r, cantus_firmus)]

    return results


def lily(results, cantus_firmus):
    conv = LilypondConverter()
    print(' '.join([str(conv.lyPitchFromPitch(p))[:-1] + '2' for p in cantus_firmus]))
    print()

    for r in results:
        print(' '.join([str(conv.lyPitchFromPitch(p))[:-1] + '2' for p in r]))


def main():
    tone = scale.MajorScale('c')
    soprano = tone.getPitches('c4', 'a5')
    alto = tone.getPitches('f3', 'd5')
    tenor = tone.getPitches('c3', 'a4')
    bass = tone.getPitches('f2', 'd4')

    cf1 = [Pitch(p) for p in ('c4', 'a3', 'g3', 'e3', 'f3', 'a3', 'g3', 'e3', 'd3', 'c3')]
    assert all(c in tenor for c in cf1)
    cf2 = [Pitch(p) for p in ('c4', 'd4', 'f4', 'e4', 'd4', 'c4', 'a3', 'b3', 'c4')]
    assert all(c in tenor for c in cf2)
    cf3 = [Pitch(p) for p in ('c4', 'e4', 'd4', 'g4', 'a4', 'g4', 'e4', 'f4', 'd4', 'c4')]
    assert all(c in soprano for c in cf3)
    cf4 = [Pitch(p) for p in ('a2', 'b2', 'c3', 'e3', 'f3', 'e3', 'c3', 'a2', 'b2', 'a2')]
    assert all(c in bass for c in cf4)

    results = do_it(cf3, bass, is_wide=True, is_cf_above=True)
    lily(results, cf3)


if __name__ == '__main__':
    main()
