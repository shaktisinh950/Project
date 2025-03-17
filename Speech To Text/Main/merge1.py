import streamlit as st
import whisper
import sounddevice as sd
import numpy as np
import wave
import tempfile
import os
import time
from difflib import SequenceMatcher

# Load the Whisper model
@st.cache_resource
def load_model():
    return whisper.load_model("base")

model = load_model()

# Function to record audio
def record_audio(duration=60, samplerate=16000, channels=1):
    st.session_state.audio_data = sd.rec(
        int(samplerate * duration),
        samplerate=samplerate,
        channels=channels,
        dtype='int16'
    )
    sd.wait()

# Function to save recorded audio
def save_audio(recording, filename, duration, samplerate=16000, channels=1):
    samples_to_keep = int(samplerate * duration)
    trimmed_recording = recording[:samples_to_keep]
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)  # 16-bit sample width
        wf.setframerate(samplerate)
        wf.writeframes(trimmed_recording.tobytes())

# Function to remove repetitive text
def remove_repetition(text):
    sentences = text.split(". ")
    unique_sentences = []
    for sentence in sentences:
        if not unique_sentences or SequenceMatcher(None, unique_sentences[-1], sentence).ratio() < 0.9:
            unique_sentences.append(sentence)
    return ". ".join(unique_sentences)

# Function to transcribe audio
def transcribe_audio(file_path):
    result = model.transcribe(file_path)
    return result["text"]
    # return remove_repetition(result['text'])

# Streamlit UI
st.title("🎙️ Audio Transcription App")
st.markdown("Upload or record an audio file, and we will transcribe it using OpenAI's Whisper model.")

# File upload
st.sidebar.header("Upload Audio File")
uploaded_file = st.sidebar.file_uploader("Choose an MP3/WAV file", type=["mp3", "wav"])

if uploaded_file is not None:
    st.subheader("🎵 Uploaded File")
    st.audio(uploaded_file, format='audio/mp3')
    if st.button("Start Transcription"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            temp_file.write(uploaded_file.getbuffer())
            temp_file_path = temp_file.name
        
        with st.spinner("Transcribing... Please wait."):
            transcription = transcribe_audio(temp_file_path)
        os.remove(temp_file_path)
        
        st.success("✅ Transcription Completed!")
        st.subheader("📄 Transcription:")
        st.text_area("Transcribed Text", transcription, height=200)
        st.download_button("📥 Download Transcription", transcription, "transcription.txt", "text/plain")

# Audio recording
st.subheader("🎤 Record and Transcribe Audio")
if 'is_recording' not in st.session_state:
    st.session_state.is_recording = False
    st.session_state.temp_audio_file_path = None

if st.button("🔴 Start/Stop Recording"):
    if st.session_state.is_recording:
        st.session_state.is_recording = False
        duration = min(int(time.time() - st.session_state.start_time), 60)
        temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        st.session_state.temp_audio_file_path = temp_audio_file.name
        save_audio(st.session_state.audio_data, st.session_state.temp_audio_file_path, duration)
        st.success(f"Recording stopped! ✅ Duration: {duration} seconds")
        transcription = transcribe_audio(st.session_state.temp_audio_file_path)
        st.subheader("📝 Transcription:")
        st.text_area("Transcribed Text", transcription, height=200)
        st.download_button("📥 Download Transcription", transcription, "transcription.txt", "text/plain")
        st.audio(st.session_state.temp_audio_file_path, format="audio/wav")
    else:
        st.session_state.is_recording = True
        st.session_state.start_time = time.time()
        record_audio()

if st.session_state.is_recording:
    elapsed_time = min(int(time.time() - st.session_state.start_time), 60)
    st.markdown(f"Recording... {elapsed_time} seconds elapsed 🔴")