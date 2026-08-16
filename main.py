import os
import sys
import time
from dotenv import load_dotenv

try:
    from openai import OpenAI
except Exception:
    print("Missing dependency 'openai'. Install dependencies with: pip install -r requirements.txt")
    sys.exit(1)

load_dotenv()

api_key = os.getenv("openaiapikey")
if not api_key:
    print("Error: 'openaiapikey' not found in environment. Add it to .env or your OS environment variables.")
    sys.exit(1)
api_key = api_key.strip().strip('"').strip("'")

model_name = os.getenv("MODEL", "openai/gpt-oss-20b:free")
max_tokens = int(os.getenv("MAX_TOKENS", "1024"))
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)

print("Type 'exit' or press Ctrl+C to quit.")
try:
    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() == "exit":
            print("Bot: Goodbye!")
            break

        try:
            start = time.perf_counter()
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": user_input}],
                max_tokens=max_tokens,
            )
            elapsed = (time.perf_counter() - start) * 1000.0
            print(f"(api latency: {elapsed:.0f} ms)")
        except Exception as e:
            print("Error calling API:", e)
            continue

        answer = None
        try:
            # common shape
            answer = response.choices[0].message.content
        except Exception:
            try:
                ch = response.choices[0]
                # dict-like choice
                if isinstance(ch, dict):
                    # new APIs sometimes use {'message': {'content': [{'type':'output_text','text':'...'}]}}
                    msg = ch.get("message") or {}
                    if isinstance(msg, dict):
                        c = msg.get("content")
                        if isinstance(c, list) and len(c) > 0:
                            first = c[0]
                            if isinstance(first, dict):
                                answer = first.get("text") or first.get("content") or str(first)
                            else:
                                answer = str(first)
                        else:
                            answer = str(c)
                    else:
                        # fallback to text field or full dict
                        answer = ch.get("text") or str(ch)
                else:
                    # object with text attr
                    answer = getattr(ch, "text", None) or str(ch)
            except Exception:
                answer = None

        # If no answer extracted, show raw response for debugging
        if not answer:
            debug = os.getenv("DEBUG", "0")
            raw = repr(response)
            if debug == "1":
                print("Bot: (no parsed content) Raw response ->", raw)
            else:
                print("Bot: (no reply parsed). Enable DEBUG=1 to see raw response.")
        else:
            print("Bot:", answer)
except KeyboardInterrupt:
    print("\nBot: Goodbye!")