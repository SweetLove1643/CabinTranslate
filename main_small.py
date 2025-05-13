import asyncio
import numpy as np
import threading
import queue
import sounddevice as sd
from faster_whisper import WhisperModel
import logging
import psutil
import torch
from time import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from translate import translate_and_tts_play
from predict import predict_emotion
from GPT_Rec import get_support_questions

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTextEdit, QListWidget
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import pyqtSlot, QMetaObject, Qt, Q_ARG
from combined_chatbot_console import chatbot_reply
import GUI
import sys



app = None
chatbot_window = None




# Thiết lập logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Kiểm tra thiết bị âm thanh
def check_audio_devices():
    devices = sd.query_devices()
    logging.info("Danh sách thiết bị âm thanh:")
    for i, device in enumerate(devices):
        logging.info(f"Thiết bị {i}: {device['name']}, Input channels: {device['max_input_channels']}")
    input_devices = [d for d in devices if d['max_input_channels'] > 0]
    if not input_devices:
        raise RuntimeError("Không tìm thấy thiết bị đầu vào âm thanh (micro)")
    logging.info(f"Thiết bị đầu vào mặc định: {input_devices[0]['name']}")
    sd.default.device = input_devices[0]['index']
    return devices

# Load mô hình Whisper
logging.info("Đang tải mô hình Whisper small...")
try:
    asr_model = WhisperModel(
        # "large-v3-turbo",  # Hoặc "medium", "small", "base" tùy thuộc vào yêu cầu
        "small",
        device="cuda" if torch.cuda.is_available() else "cpu",
        compute_type="float16" if torch.cuda.is_available() else "int8"
    )
    logging.info(f"Mô hình Faster Whisper small đã tải thành công, thiết bị: {'cuda' if torch.cuda.is_available() else 'cpu'}")
except Exception as e:
    logging.error(f"Lỗi khi tải mô hình Whisper: {e}")
    raise

# Hàng đợi cho dữ liệu âm thanh
audio_queue = queue.Queue(maxsize=10)  # Thread-safe queue
transcribe_queue = queue.Queue(maxsize=10)
stop_event = threading.Event()

# Ngưỡng năng lượng để phát hiện giọng nói
ENERGY_THRESHOLD = 0.008  # Có thể điều chỉnh tùy môi trường

# Hàm kiểm tra đoạn âm thanh có chứa giọng nói không
def is_speech(audio_chunk):
    energy = np.sqrt(np.mean(audio_chunk ** 2))
    logging.debug(f"Năng lượng đoạn âm thanh: {energy:.6f}, Ngưỡng: {ENERGY_THRESHOLD}")
    return energy > ENERGY_THRESHOLD

# Hàm ghi âm thời gian thực
def record_audio(samplerate=16000, chunk_duration=1.5): ###############################################################3333
    blocksize = int(samplerate * chunk_duration)
    logging.info(f"[Record] Bắt đầu ghi âm: tần số mẫu={samplerate} Hz, blocksize={blocksize} mẫu")

    def callback(indata, frames, time, status):
        if status:
            logging.warning(f"[Record] Trạng thái lỗi: {status}")
        if not stop_event.is_set():
            try:
                # logging.debug(f"[Record] Nhận dữ liệu âm thanh, kích thước: {indata.shape}")
                audio_queue.put_nowait(indata.copy())
            except queue.Full:
                logging.warning("[Record] Hàng đợi âm thanh đầy, bỏ qua dữ liệu")

    try:
        with sd.InputStream(samplerate=samplerate, channels=1, dtype='float32', blocksize=blocksize, callback=callback):
            logging.info("[Record] Luồng ghi âm đã khởi động")
            stop_event.wait()  # Chờ tín hiệu dừng

    except Exception as e:
        logging.error(f"[Record] Lỗi trong luồng ghi âm: {e}")
        stop_event.set()

# Hàm xử lý nhận dạng giọng nói
def stt_worker():
    audio_buffer = []
    buffer_duration = 15  # Kích thước bộ đệm tối đa: 5 giây ###############################################################3333
    samplerate = 16000  # Tần số mẫu
    max_buffer_size = int(samplerate * buffer_duration)
    last_chunk_time = time()  # Thời gian của đoạn âm thanh cuối cùng
    recognition_timeout = 2.5  # Nhận dạng sau 1.5 giây nếu không có âm thanh mới
    logging.info(f"[STT] Khởi động worker, kích thước bộ đệm tối đa: {max_buffer_size} mẫu, timeout: {recognition_timeout} giây")

    while not stop_event.is_set():
        try:
            audio_chunk = audio_queue.get(timeout=2.5) ###############################################################3333
            if audio_chunk is None:
                logging.info("[STT] Nhận tín hiệu dừng")
                break

            # Kiểm tra xem đoạn âm thanh có chứa giọng nói không
            if is_speech(audio_chunk):
                audio_buffer.append(audio_chunk)
                last_chunk_time = time()  # Cập nhật thời gian đoạn âm thanh cuối

            # Kiểm tra điều kiện để nhận dạng
            current_time = time()
            buffer_size = len(audio_buffer) * audio_chunk.size
            time_since_last_chunk = current_time - last_chunk_time

            if buffer_size >= max_buffer_size or (audio_buffer and time_since_last_chunk >= recognition_timeout):
                if audio_buffer:
                    try:
                        audio_data = np.concatenate(audio_buffer, axis=0)
                        audio_buffer = []  # Xóa bộ đệm
                        last_chunk_time = time()  # Đặt lại thời gian để tránh xử lý liên tục
                        transcribe_queue.put(audio_data)
                    except ValueError as e:
                        logging.error(f"[STT] Lỗi khi nối audio_buffer: {e}")
                else:
                    logging.debug("[STT] Bỏ qua vì audio_buffer rỗng")
                

            # Xóa các đoạn cũ nếu bộ đệm quá lớn
            while len(audio_buffer) * audio_chunk.size > max_buffer_size:
                audio_buffer.pop(0)
                logging.debug(f"[STT] Xóa đoạn cũ, số đoạn còn lại: {len(audio_buffer)}")

        except queue.Empty:
            if audio_buffer and time() - last_chunk_time >= recognition_timeout:
                if audio_buffer:
                    logging.info(f"[STT] Timeout nhận dạng: time_since_last_chunk={time() - last_chunk_time:.2f}s")
                    try:
                        audio_data = np.concatenate(audio_buffer, axis=0)
                        audio_buffer = []
                        last_chunk_time = time()
                        transcribe_queue.put(audio_data)
                    except ValueError as e:
                        logging.error(f"[STT] Lỗi khi nối audio_buffer: {e}")
                else:
                    logging.debug("[STT] Bỏ qua vì audio_buffer rỗng")

        except Exception as e:
            logging.error(f"[STT] Lỗi trong stt_worker: {e}")

# Hàm nhận dạng bất đồng bộ
def transcribe_worker(worker_id):
    executor = ThreadPoolExecutor(max_workers=1)
    while not stop_event.is_set():
        try:
            audio_data = transcribe_queue.get(timeout=2.5) ###############################################################3333
            if audio_data is None:
                logging.info("[Transcribe] Nhận tín hiệu dừng")
                break

            if not isinstance(audio_data, np.ndarray) or audio_data.size == 0:
                logging.warning("[Transcribe] Dữ liệu âm thanh không hợp lệ hoặc rỗng")
                continue

            if psutil.virtual_memory().available < 512 * 1024**2:
                logging.warning("[Transcribe] RAM thấp, bỏ qua nhận dạng")
                continue

            start_time = time()
            logging.info(f"[Transcribe-{worker_id}] Đang gọi Whisper để nhận dạng...")
            try:
                audio_data = np.squeeze(audio_data)
                #faster-wisper
                # Chạy transcribe với timeout 1 giây
                future = executor.submit(lambda: asr_model.transcribe(audio_data, language=None, condition_on_previous_text=True))
                segments, info = future.result(timeout=15) 
                text = "".join(segment.text for segment in segments).strip()
                detected_language = info.language
                processing_time = time() - start_time

                logging.info(f"[Transcribe] Kết quả nhận dạng: Ngôn ngữ={detected_language}, Văn bản='{text}', Thời gian xử lý: {processing_time:.2f}s")

                if detected_language == "vi":
                    # Nếu là tiếng Việt, dịch sang tiếng Anh
                    text_trans = translate_and_tts_play(text, "en")
                    
                    # Update main chat message (an toàn với thread)
                    QMetaObject.invokeMethod(chatbot_window, "safe_append_message", Qt.QueuedConnection, Q_ARG(str, f"[{chatbot_window.get_current_time()}] {detected_language.upper()}: {text_trans}"))
                    print(text_trans)
                    
                    
                    output = predict_emotion(text)
                    # Update emotion label
                    QMetaObject.invokeMethod(chatbot_window, "safe_update_emotion", Qt.QueuedConnection, Q_ARG(str, f"Chỉ số cảm xúc hiện tại của người nói: {output['label'] + str(output['score'])}"))
                    
                    
                    print('Emotion:', output)
                    question = get_support_questions("output", text, language="en")
                    # print('Support questions:', question)
                    # Update suggestions
                    suggestion1 = f"Gợi ý: {question}"
                    QMetaObject.invokeMethod(chatbot_window, "safe_add_suggestions1", Qt.QueuedConnection,
                                            Q_ARG(str, suggestion1))
                    
                    question2 = chatbot_reply("output","en")
                    suggestion2 = f"Gợi ý: {question2}"
                    QMetaObject.invokeMethod(chatbot_window, "safe_add_suggestions2", Qt.QueuedConnection,
                                            Q_ARG(str, suggestion2))
                    

                elif detected_language == "en":
                    output = predict_emotion(text)
                    # Update emotion label
                    QMetaObject.invokeMethod(chatbot_window, "safe_update_emotion", Qt.QueuedConnection, Q_ARG(str, f"Chỉ số cảm xúc hiện tại của người nói: {output['label'] + str(output['score'])}"))
                    
                    
                    print('Emotion:', output)
                    question = get_support_questions("output", text, language="vi")
                    suggestion1 = f"Gợi ý: {question}"
                    QMetaObject.invokeMethod(chatbot_window, "safe_add_suggestions1", Qt.QueuedConnection,
                                            Q_ARG(str, suggestion1))
                    # print('Support questions:', question)
                    text= translate_and_tts_play(text, "vi")
                    
                    # Update main chat message (an toàn với thread)
                    QMetaObject.invokeMethod(chatbot_window, "safe_append_message", Qt.QueuedConnection, Q_ARG(str, f"[{chatbot_window.get_current_time()}] {detected_language.upper()}: {text}"))
                    question2 = chatbot_reply("output","vi")
                    suggestion2 = f"Gợi ý: {question2}"
                    QMetaObject.invokeMethod(chatbot_window, "safe_add_suggestions2", Qt.QueuedConnection,
                                            Q_ARG(str, suggestion2))
                    
                    print(text)
                
                
                # Chỉ chấp nhận tiếng Anh hoặc tiếng Việt
                if detected_language in ["en", "vi"] and text:
                    print(f"[STT] ({detected_language}) {text}")

            except TimeoutError:
                logging.warning("[Transcribe] Nhận dạng vượt quá thời gian, bỏ qua")
            except Exception as e:
                logging.error(f"[Transcribe] Lỗi khi nhận dạng: {e}")
            finally:
                if 'audio_data' in locals():
                    del audio_data
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
        except queue.Empty:
            # logging.debug("[Transcribe] Hàng đợi trống, chờ dữ liệu...")
            continue
        except Exception as e:
            logging.error(f"[Transcribe] Lỗi trong transcribe_worker: {e}")
    executor.shutdown()


# Hàm chính
def main():
    global app, chatbot_window

    logging.info("Bắt đầu hệ thống nhận dạng giọng nói (Anh/Việt)")
    check_audio_devices()

    # Khởi động giao diện PyQt
    app = QApplication(sys.argv)
    chatbot_window = GUI.ChatbotWindow()
    chatbot_window.show()

    # Tạo các thread
    record_thread = threading.Thread(target=record_audio, daemon=True)
    stt_thread = threading.Thread(target=stt_worker, daemon=True)
    transcribe_thread1 = threading.Thread(target=transcribe_worker, args=(1,), daemon=True)
    transcribe_thread2 = threading.Thread(target=transcribe_worker, args=(2,), daemon=True)

    # Khởi động các thread
    record_thread.start()
    stt_thread.start()
    transcribe_thread1.start()
    transcribe_thread2.start()

    try:
        # # Giữ chương trình chạy
        # while not stop_event.is_set():
        #     threading.Event().wait(1.0)
        sys.exit(app.exec_())
    except KeyboardInterrupt:
        logging.info("Nhận tín hiệu dừng (Ctrl+C)")
        stop_event.set()
        audio_queue.put_nowait(None)
        transcribe_queue.put_nowait(None)
    except Exception as e:
        logging.error(f"Lỗi trong main: {e}")
    finally:
        logging.info("Hệ thống đã dừng")
        record_thread.join(timeout=1.0)
        stt_thread.join(timeout=1.0)
        transcribe_thread1.join(timeout=1.0)
        transcribe_thread2.join(timeout=1.0)

if __name__ == "__main__":
    main()