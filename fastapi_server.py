from fastapi import FastAPI, UploadFile, File
from faster_whisper import WhisperModel

MODEL_SIZE = "base"
LANGUAGE = "en"
DEVICE = "cuda"
MODEL = WhisperModel(MODEL_SIZE, device="cuda", compute_type="bfloat16")

app = FastAPI()

@app.post("/upload")
async def upload(audio: UploadFile = File(...)):
    segments, _ = MODEL.transcribe(audio.file, language=LANGUAGE, beam_size=5, vad_filter=True, without_timestamps=True)
    segments = list(segments)
    return {"text": " ".join(s.text.strip() for s in segments).strip() }