import sounddevice as sd
import vosk
import queue
import sys
import json
import threading
from pathlib import Path

def get_base_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent

BASE_DIR = get_base_dir()

# Model yolunu burada kontrol ediyor
MODEL_PATH = BASE_DIR / "vosk-model-small-en-us-0.15"

if not MODEL_PATH.exists():
    # Eğer ana dizinde yoksa senin bilgisayarındaki Türkçe modeli kullanmaya çalışıyor
    MODEL_PATH = Path(r"C:\Users\Umut\Downloads-no-cef-sandbox\vosk-model-small-tr-0.3")

model = vosk.Model(str(MODEL_PATH))

q = queue.Queue()
stop_listening_flag = threading.Event()

def callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))

def record_voice(prompt="🎙 Dinliyorum, efendim..."):
    """
    Sesi kaydeder ve tanınan ilk cümleyi döndürür.
    """
    print(prompt)
    rec = vosk.KaldiRecognizer(model, 16000)
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=callback):
        while not stop_listening_flag.is_set():
            try:
                data = q.get(timeout=0.1)
            except queue.Empty:
                continue
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "")
                if text.strip():
                    print("👤 Siz:", text)
                    return text
    return ""