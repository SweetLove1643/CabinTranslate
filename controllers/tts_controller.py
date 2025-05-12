# controllers/tts_controller.py
import asyncio
from models.tts_model import text_to_speech
from googletrans import Translator

def handle_tts_request(text, lang):
    voice = "vi-VN-HoaiMyNeural" if lang == "vi" else "en-US-JennyNeural"
    output_path = f"tts_{lang}.mp3"
    asyncio.run(text_to_speech(text, lang=lang, voice=voice, output_path=output_path, pitch="+0Hz"))  # Đảm bảo giá trị pitch hợp lệ
    return output_path

def translate_text(text, dest_lang):
    """Dịch văn bản sang ngôn ngữ đích."""
    translator = Translator()
    result = translator.translate(text, dest=dest_lang)
    return result.text

def handle_tts_request_with_translation(text, dest_lang):
    """Dịch văn bản và chuyển thành giọng nói."""
    translated_text = translate_text(text, dest_lang)
    return handle_tts_request(translated_text, dest_lang)