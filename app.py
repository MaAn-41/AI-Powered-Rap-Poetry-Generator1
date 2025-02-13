import streamlit as st
import whisper
import google.generativeai as genai 
import requests
import tempfile
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Load API keys from Streamlit secrets
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
PLAY_HT_API_KEY = st.secrets["PLAY_HT_API_KEY"]
PLAY_HT_USER_ID = st.secrets["PLAY_HT_USER_ID"]

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Load Whisper model
model = whisper.load_model("base")

# Function to transcribe audio
def transcribe_audio(file_path):
    result = model.transcribe(file_path)
    return result['text']

# Function to generate AI poetry
def generate_poetry(poetry_text):
    prompt = f"'{poetry_text}' ka aik behtareen aur rhyming continuation likhiye Urdu ya English mein."
    try:
        model = genai.GenerativeModel("gemini-pro") 
        response = model.generate_content(prompt)
        return response.text if response else "No poetry generated."
    except Exception as e:
        st.error(f"Error in Gemini API: {e}")
        return "Poetry generation failed."

# Function to convert text to speech and return audio file path
def text_to_speech(text):
    url = "https://api.play.ht/api/v2/tts/stream"
    headers = {
        "X-USER-ID": PLAY_HT_USER_ID,
        "AUTHORIZATION": PLAY_HT_API_KEY,
        "accept": "audio/mpeg",
        "content-type": "application/json",
    }
    data = {
        "text": text,
        "voice_engine": "PlayDialog",
        "voice": "aiq-urdu-female",
        "output_format": "mp3"
    }
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        audio_file_path = "output.mp3"
        with open(audio_file_path, 'wb') as f:
            f.write(response.content)
        return audio_file_path
    else:
        return None

# Streamlit UI
st.title("🎤 AI-Powered Rap & Poetry Generator")

option = st.radio("Choose an input method:", ["Upload Audio File"])

if option == "Upload Audio File":
    uploaded_file = st.file_uploader("Upload your freestyle rap or poetry (MP3, WAV, M4A)", type=["mp3", "wav", "m4a"])
    
    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            temp_file.write(uploaded_file.read())
            temp_path = temp_file.name
        
        st.audio(temp_path, format='audio/mp3')
        
        with st.spinner("Transcribing your poetry..."):
            poetry_text = transcribe_audio(temp_path)
            st.write("### Your Original Poetry:")
            st.write(poetry_text)
        
        with st.spinner("Generating continuation..."):
            generated_poetry = generate_poetry(poetry_text)
            st.write("### AI-Generated Continuation:")
            st.write(generated_poetry)

        with st.spinner("Generating AI narration..."):
            audio_file_path = text_to_speech(generated_poetry)

        if audio_file_path:
            st.success("Audio generated successfully!")
            st.audio(audio_file_path, format="audio/mp3")
            with open(audio_file_path, "rb") as f:
                st.download_button("Download Audio", f, file_name="poetry.mp3", mime="audio/mp3")
        else:
            st.error("Audio generation failed.")
