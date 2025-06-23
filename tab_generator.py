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

def generate_tab(pitch_estimates, notes_per_measure=16, measures_per_line=4):
    # Each pitch_estimate: {'note': 'A4', ...}
    tab_lines = [list(STRING_NAMES[i] + '|') for i in range(6)]
    note_count = 0
    measure_count = 0
    for est in pitch_estimates:
        midi = note_name_to_midi(est['note'])
        if midi is None:
            # Add a rest (dash) to all strings
            for line in tab_lines:
                line.append('-')
            note_count += 1
        else:
            pos = find_string_and_fret(midi)
            for i in range(6):
                if pos is not None and i == pos[0]:
                    line_val = str(pos[1]) if pos[1] < 10 else str(pos[1])
                    tab_lines[i].append(line_val)
                else:
                    tab_lines[i].append('-')
            note_count += 1
        # Add bar line at measure boundary
        if note_count % notes_per_measure == 0:
            for line in tab_lines:
                line.append('|')
            measure_count += 1
        # Add line break after measures_per_line
        if measure_count > 0 and measure_count % measures_per_line == 0 and note_count % notes_per_measure == 0:
            for i in range(6):
                tab_lines[i].append('\n' + STRING_NAMES[i] + '|')
    # Join lines
    # Remove trailing bar if present
    tab_strs = []
    for line in tab_lines:
        s = ''.join(line)
        if s.endswith('|'):
            s = s[:-1]
        tab_strs.append(s)
    return '\n'.join(tab_strs)

# Example usage:
if __name__ == '__main__':
    demo = [
        {'note': 'E4'}, {'note': 'F4'}, {'note': 'G4'}, {'note': 'A4'}, {'note': 'B4'}, {'note': 'C5'}, {'note': 'Unknown'}
    ] * 10
    print(generate_tab(demo, notes_per_measure=4, measures_per_line=2)) 