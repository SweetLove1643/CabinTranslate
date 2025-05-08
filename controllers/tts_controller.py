# controllers/tts_controller.py
import asyncio
from models.tts_model import text_to_speech

def handle_tts_request(text, lang):
    voice = "vi-VN-HoaiMyNeural" if lang == "vi" else "en-US-JennyNeural"
    output_path = f"tts_{lang}.mp3"
    asyncio.run(text_to_speech(text, lang=lang, voice=voice, output_path=output_path))
    return output_path