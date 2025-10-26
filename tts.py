from elevenlabs.client import ElevenLabs
from elevenlabs.play import play, stream
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("ELEVENLABS_API_KEY")
client = ElevenLabs(api_key=API_KEY)

def text_to_speech(text: str, voice_id: str, model_id: str = "eleven_flash_v2_5", output_format="mp3_44100_128"):
    audio = client.text_to_speech.convert(
        text=".  "+text,
        voice_id=voice_id,
        model_id=model_id,
        output_format=output_format
    )
    play(audio)

def text_to_speech_stream(text: str, voice_id: str = "UgBBYS2sOqTuMpoF3BR0", model_id: str = "eleven_flash_v2_5"):
    audio_stream = client.text_to_speech.stream(
        text=".  "+text,
        voice_id=voice_id,
        model_id=model_id
    )
    stream(audio_stream)