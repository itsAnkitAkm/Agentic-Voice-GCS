import sys
import time
import numpy as np
import sounddevice as sd
import scipy.io.wavfile as wav
from faster_whisper import WhisperModel


# =========================
# CONFIG
# =========================

SAMPLE_RATE = 16000
CHANNELS = 1

BLOCK_DURATION = 0.1          # seconds
SILENCE_THRESHOLD = 0.015
SILENCE_DURATION = 1.2        # stop after 1.2 sec silence
MAX_RECORDING_DURATION = 15   # safety limit

AUDIO_FILE = "recording.wav"


# =========================
# SIMPLE BEEP
# =========================

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


# =========================
# LOAD MODEL
# =========================

print("\n DRONE VOICE ASSISTANT")
print("────────────────────────────")

print("Loading speech model...")

model = WhisperModel(
    "base.en",
    device="cpu",
    compute_type="int8"
)

print("✓ Speech model ready\n")


# =========================
# RECORD WITH SILENCE DETECTION
# =========================

def record_until_silence():

    input("Press ENTER to talk...")

    # print("\n🔴 LISTENING...")

    beep()

    block_size = int(
        SAMPLE_RATE * BLOCK_DURATION
    )

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

            audio, overflowed = stream.read(
                block_size
            )

            audio_chunks.append(audio.copy())

            volume = np.sqrt(
                np.mean(audio ** 2)
            )


            # Wait until actual speech starts
            if volume > SILENCE_THRESHOLD:

                speech_started = True
                silence_time = 0

            elif speech_started:

                silence_time += BLOCK_DURATION


            # Terminal recording indicator
            if speech_started:

                print(
                    f"\r🔴 Listening... "
                    f"{time.time() - start_time:.1f}s",
                    end=""
                )

                sys.stdout.flush()


            # Stop after silence
            if (
                speech_started
                and silence_time >= SILENCE_DURATION
            ):
                break


            # Safety timeout
            if (
                time.time() - start_time
                >= MAX_RECORDING_DURATION
            ):
                break


    print("\n\n✓ Processing")

    return np.concatenate(
        audio_chunks,
        axis=0
    )


# =========================
# MAIN LOOP
# =========================

while True:

    print("\n────────────────────────────")

    audio = record_until_silence()

    wav.write(
        AUDIO_FILE,
        SAMPLE_RATE,
        audio
    )

    print("\n Transcribing...")

    segments, info = model.transcribe(
        AUDIO_FILE,
        language="en",
        vad_filter=True
    )

    text = "".join(
        segment.text
        for segment in segments
    ).strip()

    print("\nYOU SAID:")
    print(f"   {text}")

    print("\n────────────────────────────")

    again = input(
        "Press ENTER to talk again or type 'exit': "
    ).strip()

    if again.lower() == "exit":
        break