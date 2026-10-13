import wave
import sounddevice as sd
import numpy as np
from piper import PiperVoice


VOICE_MODEL = "voices/en_US-lessac-medium.onnx"

print("Loading TTS voice...")

voice = PiperVoice.load(VOICE_MODEL)

print("TTS voice ready")


def speak(text):
    """
    Convert text to speech and play it.
    """

    audio_chunks = []
    sample_rate = None

    for chunk in voice.synthesize(text):
        audio_chunks.append(chunk.audio_float_array)
        sample_rate = chunk.sample_rate

    audio = np.concatenate(audio_chunks)

    sd.play(audio, sample_rate)
    sd.wait()