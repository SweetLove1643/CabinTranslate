# models/tts_model.py
import edge_tts # type: ignore

async def text_to_speech(text, lang="vi-VN", voice="vi-VN-HoaiMyNeural", output_path="output.mp3", rate="+100%", pitch="-50%"):
    """
    Tạo giọng nói từ văn bản với các tùy chọn tối ưu hóa.

    :param text: Văn bản đầu vào.
    :param lang: Ngôn ngữ (ví dụ: "vi-VN").
    :param voice: Giọng nói (ví dụ: "vi-VN-HoaiMyNeural").
    :param output_path: Đường dẫn lưu tệp âm thanh.
    :param rate: Tốc độ nói (ví dụ: "+0%" để giữ nguyên tốc độ).
    :param pitch: Cao độ (ví dụ: "+0%" để giữ nguyên cao độ).
    """
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    await communicate.save(output_path)
    return output_path