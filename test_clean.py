import os
import sys
from pathlib import Path
import assemblyai as aai

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

env_file = Path(".env")
if env_file.exists():
    for line in env_file.read_text(encoding="utf-8", errors="ignore").splitlines():
        if line.startswith("ASSEMBLYAI_API_KEY"):
            os.environ["ASSEMBLYAI_API_KEY"] = line.split("=", 1)[1].strip("\"' ")

key = os.getenv("ASSEMBLYAI_API_KEY")
print(f"Loaded Key: {key[:8]}...")

aai.settings.api_key = key
transcriber = aai.Transcriber()
config = aai.TranscriptionConfig(language_code="am", language_detection=False)

# በ voice_output ውስጥ ያለውን PT-8849-X.mp3 ፋይል መፈተሽ
audio_path = "voice_output/PT-8849-X.mp3"

print(f"Transcribing {audio_path}...")
transcript = transcriber.transcribe(audio_path, config=config)

print("\n================ RESULT ================")
print("STATUS:", transcript.status)
print("TEXT  :", transcript.text)
print("========================================\n")