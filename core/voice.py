"""
Zemi Voice Stack
Local speech-to-text and text-to-speech
"""

import whisper
from TTS.api import TTS
import os

class VoiceHandler:
    def __init__(self):
        # Load Whisper for speech-to-text
        self.whisper_model = whisper.load_model("small")
        
        # Load Coqui TTS for text-to-speech
        self.tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")
    
    def transcribe(self, audio_file):
        """Convert speech to text"""
        result = self.whisper_model.transcribe(audio_file)
        return result["text"]
    
    def speak(self, text, output_file="output.wav"):
        """Convert text to speech"""
        self.tts.tts_to_file(text=text, file_path=output_file)
        return output_file

# Test
if __name__ == "__main__":
    voice = VoiceHandler()
    
    # Test TTS
    print("Testing text-to-speech...")
    voice.speak("Hello, I am Zemi, your local AI assistant")
    print("✓ Audio generated: output.wav")
