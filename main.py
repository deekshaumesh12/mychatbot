import os
import sys
import time
from dotenv import load_dotenv

load_dotenv()

def local_cli_response(text):
    if not text:
        return ""
    t = text.strip()
    lower = t.lower()
    if "hello" in lower or "hi" in lower:
        return "Hi — local CLI demo responder."
    if "help" in lower:
        return "Type a message and I'll echo it back (local demo)."
    return f"(local) Echo: {t}"


print("Type 'exit' or press Ctrl+C to quit.")
try:
    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() == "exit":
            print("Bot: todaloo!")
            break

        start = time.perf_counter()
        try:
            answer = local_cli_response(user_input)
            elapsed = (time.perf_counter() - start) * 1000.0
            print(f"(local latency: {elapsed:.0f} ms)")
            print("Bot:", answer)
        except Exception as e:
            print("Error generating response:", e)
except KeyboardInterrupt:
    print("\nBot: Goodbye!")