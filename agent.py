import os
import subprocess

from google import genai
from google.genai import types

from stt import listen
from tts import speak

# ============================================================
# SHELL TOOL
# ============================================================

def run_shell(command: str) -> dict:
    """
    Execute a command in the local development environment.

    This tool may be used to inspect the environment, run Python
    scripts, and communicate with the ArduPilot SITL instance through
    pymavlink.
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=os.getcwd(),
            capture_output=True,
            text=True,
            timeout=20
        )

        return {
            "return_code": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip()
        }

    except subprocess.TimeoutExpired:
        return {
            "error": "Command timed out after 20 seconds."
        }

    except Exception as error:
        return {
            "error": str(error)
        }


# ============================================================
# GEMINI CLIENT
# ============================================================

client = genai.Client()

# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """You are an ArduPilot Ground Control Station voice assistant. 
CRITICAL: To minimize latency, your responses MUST be ultra-concise (1 sentence preferred). Zero filler, zero markdown, no conversational framing. 

ENVIRONMENT:
- SITL active. Project dir: ~/Work-File/voice-drone
- MAVLink: udpin:127.0.0.1:14551 (UDP binds to 1 process at a time).
- Tool: Use `run_shell` to execute/create pymavlink scripts. Reference `mavlink_example.py`.

STRICT RULES:
1. NEVER fabricate data or command success. Always fetch live data via `run_shell`.
2. Prioritize safety. Ask for clarification if a flight command is ambiguous.
3. State results directly with units. Speak numbers naturally.
4. NO markdown, NO tables, NO lists.
5. BAN filler phrases like "I will now check...", "Command executed", or "Based on telemetry...". 

EXAMPLES:
User: "Altitude?" -> "Relative altitude is 10.2 meters."
User: "Take off to 10." -> "Takeoff sent for 10 meters."
User: "Is it armed?" -> "The aircraft is disarmed."
"""
# ============================================================
# GEMINI CONFIGURATION
# ============================================================

config = types.GenerateContentConfig(
    system_instruction=SYSTEM_PROMPT,
    tools=[run_shell]
)

chat = client.chats.create(
    model="gemini-3.5-flash",
    config=config
)

# ============================================================
# TERMINAL INTERFACE
# ============================================================

print()
print("VOICE GROUND CONTROL")
print("────────────────────────────────")
print("System online")
print()
print("[ Press ENTER to talk ]")

# ============================================================
# MAIN VOICE LOOP
# ============================================================

while True:
    try:
        input()

        # ----------------------------------------------------
        # SPEECH TO TEXT
        # ----------------------------------------------------
        user_input = listen()

        if not user_input:
            print("> No speech detected")
            print()
            print("[ Press ENTER to talk ]")
            continue

        # ----------------------------------------------------
        # DISPLAY OPERATOR SPEECH
        # ----------------------------------------------------
        print()
        print("OPERATOR")
        print(user_input)

        # ----------------------------------------------------
        # EXIT COMMAND
        # ----------------------------------------------------
        if user_input.lower().strip() in [
            "exit",
            "quit",
            "stop the system",
            "shut down"
        ]:
            print()
            print("VOICE GROUND CONTROL")
            print("System shutting down.")

            speak("System shutting down.")
            break

        # ----------------------------------------------------
        # GEMINI AGENT
        # ----------------------------------------------------
        print()
        print("> Thinking...")

        response = chat.send_message(user_input)
        response_text = response.text.strip()

        # ----------------------------------------------------
        # DISPLAY RESPONSE
        # ----------------------------------------------------
        print()
        print("GCS")
        print(response_text)

        # ----------------------------------------------------
        # TEXT TO SPEECH
        # ----------------------------------------------------
        if response_text:
            speak(response_text)

        print()
        print("────────────────────────────────")
        print("[ Press ENTER to talk ]")

    except KeyboardInterrupt:
        print()
        print()
        print("VOICE GROUND CONTROL")
        print("System interrupted.")
        break

    except Exception as error:
        print()
        print(f"> System error: {error}")
        print()
        print("[ Press ENTER to talk ]")