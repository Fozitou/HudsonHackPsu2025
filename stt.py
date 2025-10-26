import queue
import time
import numpy as np
import sounddevice as sd
import webrtcvad
from faster_whisper import WhisperModel
import warnings
import os
import logging
from collections import deque
import requests
from scipy.io.wavfile import write
import soundfile as sf


# ---- Quiet setup ----
warnings.filterwarnings("ignore")
os.environ.update({
    "TRANSFORMERS_VERBOSITY": "error",
    "DIFFUSERS_VERBOSITY": "error",
    "HF_HUB_DISABLE_PROGRESS_BARS": "1",
    "BITSANDBYTES_NOWELCOME": "1",
    "TQDM_DISABLE": "1",
    "TORCH_CPP_LOG_LEVEL": "ERROR",
    "PYTORCH_JIT_LOG_LEVEL": "ERROR",
    "CUDA_LAUNCH_BLOCKING": "0"
})
for logger_name in ["transformers", "diffusers", "torch", "accelerate"]:
    logging.getLogger(logger_name).setLevel(logging.ERROR)

# ---- Constants ----
SAMPLE_RATE = 16000
FRAME_MS = 30
SILENCE_MS = 600  # Reduced for faster response
MODEL_SIZE = "base"
LANGUAGE = "en"
DEVICE = "cuda"
COMPUTE_TYPE = "bfloat16"
WAKE_WORD = "hey"
URL = "http://127.0.0.1:8000/upload"

# Pre-calculate constants
FRAME_SAMPLES = int(SAMPLE_RATE * FRAME_MS / 1000)
SILENCE_FRAMES_LIMIT = int(SILENCE_MS / FRAME_MS)
GRACE_FRAMES = int(800 / FRAME_MS)
MAX_SPEECH_FRAMES = 600  # 18 seconds max for wake word detection

# ---- Utility functions ----
def log(msg: str, emoji: str = "🎙️"):
    print(f"[{time.strftime('%H:%M:%S')}] {emoji} {msg}")

# Pre-allocate conversion buffer to avoid repeated allocation
_conversion_buffer = np.empty(FRAME_SAMPLES, dtype=np.int16)

def to_int16_bytes(audio: np.ndarray) -> bytes:
    """Optimized float32 to int16 conversion with pre-allocated buffer"""
    np.multiply(audio, 32767, out=_conversion_buffer, casting='unsafe')
    return _conversion_buffer.tobytes()

def transcribe_audio(audio: np.ndarray):
    sf.write("example.wav", audio, SAMPLE_RATE)
    with open("example.wav", 'rb') as fobj:
        r = requests.post(URL, files={'audio': fobj}).json()
        return r["text"]
# ---- Load and warm up the model once ----
log(f"Loading Whisper '{MODEL_SIZE}' model...")
MODEL = WhisperModel(
    MODEL_SIZE, 
    device=DEVICE, 
    compute_type=COMPUTE_TYPE,
    num_workers=4,  # Parallel processing
    cpu_threads=4
)

# Warm-up with multiple sizes to cache different batch sizes
for size in [SAMPLE_RATE // 4, SAMPLE_RATE // 2, SAMPLE_RATE]:
    _ = MODEL.transcribe(np.zeros(size, dtype=np.float32))
log("Model ready", "✅")

# ---- Main function ----
def listen_and_transcribe(wake_word: str = WAKE_WORD) -> str:
    """Optimized listener with faster wake word detection and recording"""
    
    vad = webrtcvad.Vad(2)
    audio_q = queue.Queue(maxsize=300)
    
    def audio_callback(indata, frames, time_info, status):
        """Minimalist callback - just copy data"""
        audio_q.put(indata[:, 0].copy())
    
    log(f"Listening for '{wake_word}'...")
    
    # Use deque with maxlen for automatic memory management
    speech_buffer = deque(maxlen=MAX_SPEECH_FRAMES)
    recording_buffer = []
    recording = False
    silence_count = 0
    frames_since_start = 0
    
    # Pre-allocate numpy array for faster concatenation
    concat_buffer = np.empty(MAX_SPEECH_FRAMES * FRAME_SAMPLES, dtype=np.float32)
    
    with sd.InputStream(
        samplerate=SAMPLE_RATE, 
        channels=1, 
        dtype="float32",
        blocksize=FRAME_SAMPLES, 
        callback=audio_callback,
        latency='low'  # Request low latency
    ):
        while True:
            frame = audio_q.get()
            is_speech = vad.is_speech(to_int16_bytes(frame), SAMPLE_RATE)
            
            if recording:
                frames_since_start += 1
                recording_buffer.append(frame)
                
                # Early termination check for silence during recording
                if is_speech:
                    silence_count = 0
                else:
                    silence_count += 1
                    if frames_since_start > GRACE_FRAMES and silence_count >= SILENCE_FRAMES_LIMIT:
                        if recording_buffer:
                            log("Processing...", "⏹️")
                            audio = np.concatenate(recording_buffer)
                            text = transcribe_audio(audio)
                            log("Done", "✅")
                            return text
                        recording = False
                        silence_count = 0
                        frames_since_start = 0
                        log(f"Listening for '{wake_word}'...")
            else:
                # Wake word detection phase
                if is_speech:
                    silence_count = 0
                    speech_buffer.append(frame)
                else:
                    silence_count += 1
                    
                    if speech_buffer and silence_count >= 2:
                        num_frames = len(speech_buffer)
                        
                        audio_len = num_frames * FRAME_SAMPLES
                        for i, f in enumerate(speech_buffer):
                            start = i * FRAME_SAMPLES
                            concat_buffer[start:start + FRAME_SAMPLES] = f
                        audio = concat_buffer[:audio_len]
                        
                        text = transcribe_audio(audio).lower()
                        if text and wake_word in text:
                            recording = True
                            recording_buffer = list(speech_buffer)
                            silence_count = 0
                            frames_since_start = 0
                            log("Recording started...", "🎬")
                        
                        speech_buffer.clear()