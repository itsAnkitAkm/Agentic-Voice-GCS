import time
import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel


SAMPLE_RATE = 16000
CHANNELS = 1
BLOCK_DURATION = 0.1
SILENCE_THRESHOLD = 0.015
SILENCE_DURATION = 1.2
MAX_RECORDING_DURATION = 15


print("Loading speech model...")

model = WhisperModel(
    "base.en",
    device="cpu",
    compute_type="int8"
)

print("Speech model ready")


def beep(frequency=800, duration=0.15):
    t = np.linspace(
        0,
        duration,
        int(SAMPLE_RATE * duration),
        endpoint=False
    )

    tone = 0.3 * np.sin(
        2 * np.pi * frequency * t
    )

    sd.play(tone, SAMPLE_RATE)
    sd.wait()


def record_until_silence():
    print("> Listening...")
    beep()

    block_size = int(SAMPLE_RATE * BLOCK_DURATION)

    audio_chunks = []
    silence_time = 0
    start_time = time.time()
    speech_started = False

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="float32",
        blocksize=block_size
    ) as stream:

        while True:
            audio, overflowed = stream.read(block_size)
            audio_chunks.append(audio.copy())

            volume = np.sqrt(np.mean(audio ** 2))

            if volume > SILENCE_THRESHOLD:
                speech_started = True
                silence_time = 0

            elif speech_started:
                silence_time += BLOCK_DURATION

            if (
                speech_started
                and silence_time >= SILENCE_DURATION
            ):
                break

            if (
                time.time() - start_time
                >= MAX_RECORDING_DURATION
            ):
                break

    print("> Processing...")

    return np.concatenate(audio_chunks, axis=0)


def listen():
    """
    Listen from microphone and return transcribed text.
    """

    audio = record_until_silence()

    print("> Transcribing...")

    segments, info = model.transcribe(
        audio.flatten(),
        language="en",
        vad_filter=True
    )

    text = "".join(
        segment.text
        for segment in segments
    ).strip()

    return text