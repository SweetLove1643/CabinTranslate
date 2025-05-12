# views/tts_view.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from controllers.tts_controller import handle_tts_request

def tts_page():
    st.title("Text to Speech (TTS)")
    text = st.text_area("Nhập văn bản")
    lang = st.selectbox("Ngôn ngữ", ["vi", "en"])
    if st.button("Chuyển thành giọng nói"):
        audio_path = handle_tts_request(text, lang)
        audio_file = open(audio_path, "rb")
        st.audio(audio_file.read(), format="audio/mp3")
        
if __name__ == "__main__":
    tts_page()