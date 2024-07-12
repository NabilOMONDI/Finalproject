import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from music21 import converter, instrument, note, chord, midi
from keras.models import load_model

# Load trained model
model = load_model('/Users/nabilomondi/Documents/Finalproject/my_model.h5')

st.title("LSTM MIDI Music Generation")

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
    st.write("### Original MIDI File Notes")
    original_notes = parse_midi(uploaded_file)
    st.write(original_notes)

    # Assuming your model expects a certain input shape, prepare your input data here
    # For example, generating a sequence from the original notes
    # model_input = prepare_input(original_notes)

    # Generate music using the model (dummy data here, replace with actual model prediction)
    # prediction_output = model.predict(model_input)
    prediction_output = original_notes[:100]  # Replace with your model output

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
