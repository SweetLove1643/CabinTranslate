import time
import os
import platform
from controllers.tts_controller import handle_tts_request, handle_tts_request_with_translation

if __name__ == "__main__":
    text = "Nhằm nâng cao tinh thần học hỏi, làm việc nhóm, tự học, khả năng truyền đạt thuyết trình cũng như chuẩn bị kiến thức cho các cuộc thi."
    dest_lang = "en"

    # # TTS trực tiếp (không dịch)
    # print("\n--- Chạy TTS trực tiếp (không dịch) ---")
    # start = time.time()
    # audio_path = handle_tts_request(text, dest_lang)
    # end = time.time()
    # print(f"Time for handle_tts_request: {end - start:.4f} seconds")
    # with open(audio_path, "rb") as src, open("output_tts.mp3", "wb") as dst:
    #     dst.write(src.read())
    # print("Đã lưu file output_tts.mp3")

    # Dịch + TTS
    print("\n--- Chạy dịch + TTS ---")
    start = time.time()
    audio_path = handle_tts_request_with_translation(text, dest_lang)
    end = time.time()
    print(f"Time for handle_tts_request_with_translation: {end - start:.4f} seconds")
    with open(audio_path, "rb") as src, open("output_translated.mp3", "wb") as dst:
        dst.write(src.read())
    print("Đã lưu file output_translated.mp3")

    # # Đọc file âm thanh đầu ra (in ra kích thước file)
    # tts_size = os.path.getsize("output_tts.mp3")
    # translated_size = os.path.getsize("output_translated.mp3")
    # print(f"Kích thước file output_tts.mp3: {tts_size} bytes")
    # print(f"Kích thước file output_translated.mp3: {translated_size} bytes")

    # Phát file âm thanh đầu ra (Windows, dùng pygame)
    try:
        import pygame
        pygame.mixer.init()
        pygame.mixer.music.load("output_translated.mp3")
        pygame.mixer.music.play()
        print("Đang phát file output_translated.mp3...")
        while pygame.mixer.music.get_busy():
            continue
    except Exception as e:
        print(f"Lỗi khi phát âm thanh: {e}")
