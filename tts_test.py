import subprocess
import sounddevice as sd
import soundfile as sf

TEXT = "Hello. ClearSky voice system is online."

subprocess.run(
    [
        "python",
        "-m",
        "piper",
        "-m",
        "en_US-lessac-medium",
        "--data-dir",
        "voices",
        "-f",
        "speech.wav",
        "--",
        TEXT
    ],
    check=True
)

audio, sample_rate = sf.read("speech.wav")

sd.play(audio, sample_rate)
sd.wait()