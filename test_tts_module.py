from tts import speak

print("CLEARSKY TTS TEST")
print("------------------")

while True:

    text = input("\nEnter text to speak (or 'exit'): ")

    if text.lower() == "exit":
        break

    speak(text)