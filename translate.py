import asyncio
import pygame
import time
from controllers.tts_controller import handle_tts_request_with_translation

def translate_and_tts_play(text: str, lang: str):
    print("\n--- Chạy dịch + TTS ---")
    start = time.time()
    translated_text, audio_path = asyncio.run(handle_tts_request_with_translation(text, lang))
    end = time.time()
    print(f"Time for handle_tts_request_with_translation: {end - start:.4f} seconds")

    output_file = "output_translated.mp3"
    with open(audio_path, "rb") as src, open(output_file, "wb") as dst:
        dst.write(src.read())
    print(f"Đã lưu file {output_file}")

    try:
        pygame.mixer.init()
        pygame.mixer.music.load(output_file)
        pygame.mixer.music.play()
        print(f"Đang phát file {output_file}...")
        while pygame.mixer.music.get_busy():
            continue
        # ✅ Giải phóng sau khi phát xong:
        pygame.mixer.music.stop()
        pygame.mixer.quit()
    except Exception as e:
        print(f"Lỗi khi phát âm thanh: {e}")
    return translated_text

if __name__ == "__main__":
    text = "Nhằm nâng cao tinh thần học hỏi, làm việc nhóm, tự học, khả năng truyền đạt thuyết trình cũng như chuẩn bị kiến thức cho các cuộc thi."
    dest_lang = "en"
    a = translate_and_tts_play(text, dest_lang)
    print(a)
    b = translate_and_tts_play("Diabetes mellitus, a major metabolic disorder caused by insulin dysfunction, is the third leading cause of death globally. Early diagnosis plays an important task for enhancing treatment effectiveness, preventing complications, and reducing healthcare costs. This study introduces a deep learning-based framework for diabetes prediction based on key clinical features such as BMI, age, and insulin levels.", "vi")
    print(b)
