# views/tts_view.py
import sys
import os
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from controllers.tts_controller import handle_tts_request
from utils.config import measure_execution_time

@measure_execution_time
def tts_page():
    st.title("Text to Speech (TTS)")
    text = st.text_area("Nhập văn bản")
    lang = st.selectbox("Ngôn ngữ", ["vi", "en"])
    if st.button("Chuyển thành giọng nói"):
        start_tts = time.time()
        audio_data = handle_tts_request(text, lang)  # Trả về dữ liệu âm thanh dạng bytes
        end_tts = time.time()
        print(f"Time for handle_tts_request: {end_tts - start_tts:.4f} seconds")

        start_audio = time.time()
        st.audio(audio_data, format="audio/mp3")  # Định dạng chính xác là mp3, không phải wav
        end_audio = time.time()
        print(f"Time for st.audio: {end_audio - start_audio:.4f} seconds")
        
if __name__ == "__main__":
    tts_page()