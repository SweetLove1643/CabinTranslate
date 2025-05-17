import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import av
import whisper
import numpy as np
import queue
import tempfile
import os
import threading
import time
from datetime import datetime

# Tiêu đề ứng dụng
st.title("Chuyển đổi giọng nói thành văn bản Real-time với Whisper")

# Tải mô hình Whisper
@st.cache_resource
def load_whisper_model():
    return whisper.load_model("tiny")  # Sử dụng mô hình tiny để tối ưu tốc độ

model = load_whisper_model()

# Danh sách ngôn ngữ hỗ trợ
language_options = {
    "Tiếng Việt": "vi",
    "Tiếng Anh": "en",
    "Tiếng Trung": "zh",
    "Tiếng Nhật": "ja",
    "Tiếng Hàn": "ko",
    "Tiếng Pháp": "fr",
    "Tiếng Tây Ban Nha": "es",
    "Tiếng Đức": "de",
}

# Tùy chọn ngôn ngữ
selected_language = st.selectbox("Chọn ngôn ngữ:", list(language_options.keys()))
language_code = language_options[selected_language]

# Hàng đợi để lưu trữ các khung âm thanh
audio_queue = queue.Queue()

# Biến trạng thái để lưu văn bản
if "transcriptions" not in st.session_state:
    st.session_state.transcriptions = []

# Callback để xử lý khung âm thanh
def audio_frame_callback(frame: av.AudioFrame) -> av.AudioFrame:
    audio_queue.put(frame)
    return frame

# Tạo luồng WebRTC để ghi âm
ctx = webrtc_streamer(
    key="speech-to-text",
    mode=WebRtcMode.SENDONLY,
    audio_frame_callback=audio_frame_callback,
    rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
    media_stream_constraints={"audio": True, "video": False},
)

# Hàm xử lý âm thanh liên tục
def process_audio_continuously():
    while st.session_state.get("running", False):
        if not audio_queue.empty():
            # Lấy các khung âm thanh trong khoảng 5 giây
            audio_frames = []
            start_time = time.time()
            while time.time() - start_time < 5.0 and not audio_queue.empty():
                frame = audio_queue.get()
                audio_frames.append(frame)

            if audio_frames:
                # Chuyển đổi các khung âm thanh thành mảng numpy
                audio_data = []
                for frame in audio_frames:
                    data = frame.to_ndarray()
                    audio_data.append(data)

                audio_data = np.concatenate(audio_data, axis=1)
                # Chuyển đổi thành định dạng phù hợp cho Whisper (mono, 16kHz)
                audio_data = audio_data.mean(axis=0).astype(np.float32)

                # Lưu tạm thời thành tệp WAV
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                    import scipy.io.wavfile
                    scipy.io.wavfile.write(temp_file.name, 16000, audio_data)
                    temp_file_path = temp_file.name

                # Chuyển đổi âm thanh thành văn bản
                result = model.transcribe(temp_file_path, language=language_code)
                text = result["text"].strip()

                # Xóa tệp tạm
                os.remove(temp_file_path)

                if text:
                    # Thêm văn bản vào trạng thái với thời gian
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    st.session_state.transcriptions.append(f"[{timestamp}] {text}")

        # Nghỉ ngắn để tránh chiếm quá nhiều CPU
        time.sleep(0.1)

# Quản lý luồng xử lý liên tục
if "processing_thread" not in st.session_state:
    st.session_state.processing_thread = None
    st.session_state.running = False

# Nút điều khiển
if st.button("Bắt đầu xử lý liên tục"):
    if not st.session_state.running:
        st.session_state.running = True
        st.session_state.processing_thread = threading.Thread(target=process_audio_continuously)
        st.session_state.processing_thread.daemon = True
        st.session_state.processing_thread.start()
        st.write("Đã bắt đầu xử lý liên tục...")

if st.button("Dừng xử lý"):
    st.session_state.running = False
    if st.session_state.processing_thread:
        st.session_state.processing_thread = None
    st.write("Đã dừng xử lý.")

# Hiển thị văn bản đã chuyển đổi
st.write("**Văn bản được chuyển đổi:**")
for transcription in st.session_state.transcriptions:
    st.write(transcription)

# Nút xóa lịch sử
if st.button("Xóa lịch sử văn bản"):
    st.session_state.transcriptions = []
    st.write("Lịch sử văn bản đã được xóa.")

# Hướng dẫn
st.markdown("""
### Hướng dẫn:
1. Chọn ngôn ngữ từ menu dropdown.
2. Nhấn nút "Start" để bắt đầu ghi âm từ micro.
3. Nhấn "Bắt đầu xử lý liên tục" để tự động chuyển đổi âm thanh mỗi 5 giây.
4. Văn bản được chuyển đổi sẽ hiển thị bên dưới kèm thời gian.
5. Nhấn "Dừng xử lý" để dừng xử lý liên tục.
6. Nhấn "Xóa lịch sử văn bản" để xóa các văn bản đã chuyển đổi.
7. Nhấn "Stop" trên giao diện ghi âm để dừng micro.
""")