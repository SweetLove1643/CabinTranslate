import asyncio
from models.tts_model import text_to_speech
from deep_translator import GoogleTranslator

async def handle_tts_request(text, lang):
    """Chuyển văn bản sang giọng nói và lưu file mp3."""
    voice = "vi-VN-HoaiMyNeural" if lang == "vi" else "en-US-JennyNeural"
    output_path = f"tts_{lang}.mp3"
    await text_to_speech(text, lang=lang, voice=voice, output_path=output_path, pitch="+0Hz")
    return output_path

async def handle_tts_request_with_translation(text, dest_lang):
    """Dịch văn bản và chuyển thành giọng nói."""
    translated_text = translate_text(text, dest_lang)
    audio_path = await handle_tts_request(translated_text, dest_lang)
    return translated_text, audio_path

def translate_text(text, dest_lang):
    """Dịch văn bản sang ngôn ngữ đích bằng deep-translator."""
    translated_text = GoogleTranslator(source='auto', target=dest_lang).translate(text)
    return translated_text
