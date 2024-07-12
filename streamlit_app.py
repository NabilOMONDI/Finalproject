import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from music21 import converter, instrument, note, chord, midi
from keras.models import load_model
import io
from keras.utils import pad_sequences

# Load your trained model
model = load_model('/Users/nabilomondi/Documents/Finalproject/my_model.h5')

st.title("LSTM MIDI Music Generation")
st.write("Model input shape:", model.input_shape)

# Function to parse MIDI file and extract notes
def parse_midi(file):
    notes = []
    midi_data = converter.parse(file)
    notes_to_parse = None

    try:  # File has instrument parts
        parts = instrument.partitionByInstrument(midi_data)
        notes_to_parse = parts.parts[0].recurse()
    except:  # File has notes in a flat structure
        notes_to_parse = midi_data.flat.notes

    for element in notes_to_parse:
        if isinstance(element, note.Note):
            notes.append(str(element.pitch))
        elif isinstance(element, chord.Chord):
            notes.append('.'.join(str(n) for n in element.normalOrder))

    return notes

# Function to prepare input sequences for the model
def prepare_sequences(notes, sequence_length=100, num_features=4):
    pitchnames = sorted(set(item for item in notes))
    note_to_int = {note: number for number, note in enumerate(pitchnames)}

    # Create input sequences and corresponding outputs
    network_input = []
    for i in range(0, len(notes) - sequence_length):
        sequence_in = notes[i:i + sequence_length]
        network_input.append([note_to_int[char] for char in sequence_in])

    # Pad sequences to ensure they all have the same length and number of features
    network_input = pad_sequences(network_input, maxlen=sequence_length, dtype='float32')
    network_input = np.reshape(network_input, (len(network_input), sequence_length, num_features))

    return network_input, note_to_int

# Function to generate MIDI file from notes
def generate_midi(prediction_output, output_file):
    offset = 0
    output_notes = []

    for pattern in prediction_output:
        if ('.' in pattern) or pattern.isdigit():
            notes_in_chord = pattern.split('.')
            notes = []
            for current_note in notes_in_chord:
                new_note = note.Note(int(current_note))
                new_note.storedInstrument = instrument.Piano()
                notes.append(new_note)
            new_chord = chord.Chord(notes)
            new_chord.offset = offset
            output_notes.append(new_chord)
        else:
            new_note = note.Note(pattern)
            new_note.offset = offset
            new_note.storedInstrument = instrument.Piano()
            output_notes.append(new_note)

        offset += 0.5

    midi_stream = midi.stream.Stream(output_notes)
    midi_stream.write('midi', fp=output_file)

# File uploader
uploaded_file = st.file_uploader("Upload a MIDI file", type=["mid", "midi"])

if uploaded_file is not None:
    try:
        # Use io.BytesIO to handle file-like object
        midi_data = io.BytesIO(uploaded_file.read())
        original_notes = parse_midi(midi_data)
        
        st.write("### Original MIDI File Notes")
        st.write(original_notes)

        # Prepare input sequences for the model
        network_input, note_to_int = prepare_sequences(original_notes, sequence_length=100, num_features=4)

        # Generate music using the model
        prediction_output = []
        int_to_note = {number: note for note, number in note_to_int.items()}
        pattern = network_input[0]  # Start with the first sequence
        pattern = np.reshape(pattern, (1, len(pattern), 1))
        pattern = pattern / float(len(note_to_int))

        for _ in range(100):  # Generate 100 notes
            prediction = model.predict(pattern, verbose=0)
            index = np.argmax(prediction)
            result = int_to_note[index]
            prediction_output.append(result)

            pattern = np.append(pattern[:,1:,:], [[index]], axis=1)
            pattern = pattern / float(len(note_to_int))

        st.write("### Generated MIDI File Notes")
        st.write(prediction_output)

        # Save and display the generated MIDI file
        output_file = 'generated_music.mid'
        generate_midi(prediction_output, output_file)
        st.audio(output_file, format='audio/midi')

        # Visualization
        st.write("### Notes Distribution")
        fig, ax = plt.subplots()
        ax.hist([note for note in original_notes if note.isdigit()], bins=50, alpha=0.5, label='Original')
        ax.hist([note for note in prediction_output if note.isdigit()], bins=50, alpha=0.5, label='Generated')
        ax.legend(loc='upper right')
        st.pyplot(fig)
    
    except Exception as e:
        st.error(f"An error occurred while processing the MIDI file: {e}")
