# Simple single-note guitar tab generator
# Usage: generate_tab(pitch_estimates) -> str

# Standard tuning (EADGBE), string 6 is low E
STANDARD_TUNING = [40, 45, 50, 55, 59, 64]  # MIDI numbers for E2, A2, D3, G3, B3, E4
STRING_NAMES = ['E', 'A', 'D', 'G', 'B', 'e']

NOTE_TO_MIDI = {
    'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11
}

def note_name_to_midi(note):
    # e.g. 'A4' -> 69
    if note == 'Unknown':
        return None
    if len(note) < 2:
        return None
    name = note[:-1]
    octave = int(note[-1])
    if name not in NOTE_TO_MIDI:
        return None
    return 12 * (octave + 1) + NOTE_TO_MIDI[name]

def find_string_and_fret(midi_num):
    # Return (string_index, fret) for lowest fret possible
    best = None
    for i, open_midi in enumerate(STANDARD_TUNING):
        fret = midi_num - open_midi
        if 0 <= fret <= 20:  # reasonable fret range
            if best is None or fret < best[1]:
                best = (i, fret)
    return best  # (string_index, fret) or None

def generate_tab(pitch_estimates):
    # Each pitch_estimate: {'note': 'A4', ...}
    tab_lines = [list(STRING_NAMES[i] + '|') for i in range(6)]
    for est in pitch_estimates:
        midi = note_name_to_midi(est['note'])
        if midi is None:
            # Add a rest (dash) to all strings
            for line in tab_lines:
                line.append('-')
            continue
        pos = find_string_and_fret(midi)
        if pos is None:
            for line in tab_lines:
                line.append('-')
            continue
        for i in range(6):
            if i == pos[0]:
                line_val = str(pos[1]) if pos[1] < 10 else str(pos[1])
                tab_lines[i].append(line_val)
            else:
                tab_lines[i].append('-')
    # Join lines
    return '\n'.join(''.join(line) for line in tab_lines)

# Example usage:
if __name__ == '__main__':
    # Fake pitch estimates for demo
    demo = [
        {'note': 'E4'}, {'note': 'F4'}, {'note': 'G4'}, {'note': 'A4'}, {'note': 'B4'}, {'note': 'C5'}, {'note': 'Unknown'}
    ]
    print(generate_tab(demo)) 