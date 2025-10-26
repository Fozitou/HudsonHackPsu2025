import time
from gemini_llm import respond
from stt import listen_and_transcribe
from tts import text_to_speech_stream

WAKE_WORD = "hey"

def main():
    while True:
        try:
            user_input = listen_and_transcribe(wake_word=WAKE_WORD)
            if not user_input:
                continue

            print(f"🎙️ You said: {user_input}")

            # user_input = input("Prompt: ")

            # Get model response
            response_text = respond(user_input) # type: ignore
            print(f"💬 Assistant: {response_text}")

            # Convert response to speech and play
            text_to_speech_stream(response_text, "UgBBYS2sOqTuMpoF3BR0", "eleven_flash_v2_5")

        except KeyboardInterrupt:
            print("\n👋 Bye!")
            break
        except Exception as e:
            print(f"⚠️ Error: {e}")
            time.sleep(1)


if __name__ == "__main__":
    main()
