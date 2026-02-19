import subprocess
import tempfile
import os

VOICE_MODEL = "/Users/zemi/ZemiV1/voices/en_US-arctic-medium.onnx"

def speak(text):
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            tmp_path = f.name
        
        subprocess.run(
            ["piper", "--model", VOICE_MODEL, "--output_file", tmp_path],
            input=text.encode(),
            capture_output=True
        )
        subprocess.run(["afplay", tmp_path])
        os.unlink(tmp_path)
    except Exception as e:
        print(f"Voice error: {e}")
