from stt import listen

print("\nCLEARSKY VOICE INTERFACE")
print("──────────────────────────")

while True:

    input("\n[ Press ENTER to talk ]")

    text = listen()

    if text:
        print("\nYOU")
        print(text)