# models/tts_model.py
import edge_tts # type: ignore

async def text_to_speech(text, lang="vi-VN", voice="vi-VN-HoaiMyNeural", output_path="output.mp3"):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)
    return output_path