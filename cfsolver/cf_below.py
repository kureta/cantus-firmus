from music21.interval import DiatonicInterval

perfect_fifths = [
    DiatonicInterval('perfect', 5),
    DiatonicInterval('perfect', 12),
]

perfect_octaves = [
    DiatonicInterval('perfect', 1),
    DiatonicInterval('perfect', 8),
    DiatonicInterval('perfect', 15),
]

perfect_intervals = perfect_fifths + perfect_octaves

cantizans = [
    DiatonicInterval('major', 7),
    DiatonicInterval('major', 14),
]

tenorizans = [
    DiatonicInterval('major', 2),
    DiatonicInterval('major', 9),
    DiatonicInterval('major', 16),
]

vertical_intervals = [
    DiatonicInterval('major', 3),
    DiatonicInterval('minor', 3),
    DiatonicInterval('perfect', 5),
    DiatonicInterval('major', 6),
    DiatonicInterval('minor', 6),
    DiatonicInterval('perfect', 8),
    DiatonicInterval('major', 10),
    DiatonicInterval('minor', 10),
]

optional_verticals = [
    DiatonicInterval('perfect', 12),
    DiatonicInterval('major', 13),
    DiatonicInterval('minor', 13),
    DiatonicInterval('perfect', 15),
    DiatonicInterval('major', 17),
    DiatonicInterval('minor', 17),
]
