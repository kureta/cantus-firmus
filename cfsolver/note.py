import operator
from functools import reduce

from typing_extensions import Self

note_names = {'c': 0, 'd': 2, 'e': 4, 'f': 5, 'g': 7, 'a': 9, 'b': 11}
major_family = (2, 2, 1, 2, 2, 2, 1)
scale_names = ['major', 'dorian', 'phrygian', 'lydian', 'mixolydian', 'aeolian', 'locrian']
scales = {sn: major_family[idx:] + major_family[:idx] for idx, sn in enumerate(scale_names)}


class Note:
    def __init__(self, diatonic: int, chromatic: int, octave: int = 0):
        self.diatonic: int = diatonic % 7
        self.chromatic: int = chromatic % 12
        self.octave: int = octave + chromatic // 12

    @property
    def midi(self) -> int:
        return self.octave * 12 + self.chromatic

    def __repr__(self) -> str:
        return f'{self.__class__}:\n' \
               f'step: {self.diatonic}\n' \
               f'pc: {self.chromatic}\n' \
               f'octave: {self.octave}\n'

    def __eq__(self, other: Self) -> bool:
        return self.diatonic == other.diatonic and self.chromatic == other.chromatic and self.octave == other.octave

    def __gt__(self, other: Self) -> bool:
        return self.midi > other.midi

    def __add__(self, other: Self) -> Self:
        diatonic = (self.diatonic + other.diatonic) % 7
        midi = self.midi + other.midi
        chromatic = midi % 12
        octave = midi // 12

        return Note(diatonic, chromatic, octave)

    def __sub__(self, other: Self) -> Self:
        diatonic = (self.diatonic - other.diatonic) % 7
        midi = self.midi - other.midi
        chromatic = midi % 12
        octave = midi // 12

        return Note(diatonic, chromatic, octave)

    def __neg__(self) -> Self:
        return Note(-self.diatonic, -self.chromatic, -self.octave)

    def __abs__(self) -> Self:
        return Note(abs(self.diatonic), abs(self.chromatic), abs(self.octave))


def parse_note(note: str) -> int:
    """Parse note name into pitch-class"""
    base = note[0]
    base_pc = note_names[base]
    accidentals = note[1:]
    n_acc = map(lambda x: {'f': -1, 's': 1}[x], accidentals)
    acc = sum(n_acc)
    pc = base_pc + acc

    return pc


def build_note(pc: int, name: str) -> str:
    base_pc = note_names[name]
    diff = base_pc - pc
    if diff < 0:
        accidental = ''.join(['f'] * abs(diff))
    else:
        accidental = ''.join(['s'] * diff)

    return name + accidental


def generate_tone(note: str, scale_name: str):
    base_pc = parse_note(note)
    scale = generate_scale(scale_name, base_pc)
    tone = []
    for pitch in range(128):
        if (pc := pitch % 12) in scale:
            octave = pitch // 12
            diatonic = scale.index(pc)
            tone.append(Note(diatonic, pc, octave))

    return tone


ranges = {
    'soprano': range(60, 82),
    'alto': range(53, 75),
    'tenor': range(48, 70),
    'bass': range(41, 63),
}


def generate_scale(name, base_note=0):
    pc = base_note
    scale = []

    for step in scales[name]:
        scale.append(pc)
        pc = (pc + step) % 12

    return scale


def generate_register(voice, name, base_note=0):
    scale = generate_scale(name, base_note)

    register = []
    for pitch in ranges[voice]:
        pc = pitch % 12
        octave = (pitch // 12) - 1
        if pc in scale:
            diatonic = scale.index(pc)
            register.append(Note(diatonic, pc, octave))

    return register


vertical_intervals = [
    Note(2, 3),
    Note(2, 4),
    Note(4, 7),
    Note(5, 8),
    Note(5, 9),
    Note(0, 0, 1),
    Note(2, 3, 1),
]


def main():
    cf = [Note()]
    notes = generate_register('tenor', 'aeolian', 2)

    print('=========================')
    print([n for n in notes if n - Note(6, 0, 4) in vertical_intervals])


if __name__ == '__main__':
    main()
