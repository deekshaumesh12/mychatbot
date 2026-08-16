import os

import gradio as gr
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("openaiapikey")
if not api_key:
    raise RuntimeError("openaiapikey not found. Add it to .env or your environment variables.")

api_key = api_key.strip().strip('"').strip("'")
model_name = os.getenv("MODEL", "openai/gpt-oss-20b:free")
max_tokens = int(os.getenv("MAX_TOKENS", "256"))

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)


def build_messages(history, user_message):
    messages = []
    for item in history or []:
        if isinstance(item, dict):
            role = item.get("role")
            content = item.get("content")
            if role in {"user", "assistant"} and content is not None:
                messages.append({"role": role, "content": content})
        elif isinstance(item, tuple) and len(item) == 2:
            user_content, assistant_content = item
            if user_content:
                messages.append({"role": "user", "content": user_content})
            if assistant_content:
                messages.append({"role": "assistant", "content": assistant_content})

    messages.append({"role": "user", "content": user_message})
    return messages


def get_response(message, history):
    if not message or not message.strip():
        return ""

    try:
        messages = build_messages(history, message)
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            max_tokens=max_tokens,
        )

        answer = response.choices[0].message.content
        if answer is None:
            return "I did not receive a valid reply from the model."
        return answer
    except Exception as exc:
        return f"Error: {exc}"


css = """
    body {
        background: #f4dfe7;
        font-family: 'Shrikhand', cursive;
    }
    #chat-title {
        text-align: left;
        font-size: 5rem;
        line-height: 1;
        font-weight: 900;
        color: #000000;
        margin: 10px 0 18px 0;
        letter-spacing: -0.06em;
        font-family: 'Shrikhand', cursive;
    }
    .gradio-container {
        max-width: 1200px !important;
        padding: 14px 30px 30px 30px !important;
        background: #f4dfe7;
    }
    .panel-wrap {
        display: flex;
        flex-direction: column;
        gap: 18px;
    }
    .main-chat {
        width: 100%;
        min-height: 380px;
        background: #5b4355;
        border: 4px solid #000000;
        border-radius: 28px;
        padding: 18px;
        box-sizing: border-box;
    }
    .chat-input-wrap {
        width: 100%;
        background: #bb8eb6;
        border: 4px solid #000000;
        border-radius: 28px;
        padding: 14px 16px;
        min-height: 70px;
        box-sizing: border-box;
        font-family: 'Shrikhand', cursive;
        font-size: 1.5rem;
        color: #000000;
    }
    .chat-input-wrap textarea,
    .chat-input-wrap input {
        color: #000000 !important;
        background: transparent !important;
        font-family: 'Shrikhand', cursive !important;
        font-size: 1.5rem !important;
    }
    .chat-input-wrap::placeholder {
        color: rgba(0, 0, 0, 0.7);
        font-family: 'Shrikhand', cursive;
        font-size: 1.5rem;
    }
    .action-row {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 30px;
        margin-top: 20px;
    }
    .action-button {
        width: 250px;
        height: 68px;
        border-radius: 26px !important;
        border: 4px solid #000000 !important;
        background: #000000 !important;
        color: #ffffff !important;
        font-size: 2.1rem !important;
        font-weight: 900 !important;
        font-family: 'Shrikhand', cursive !important;
        text-transform: lowercase;
    }
    .clear-button {
        background: #000000 !important;
    }
    .chatbot {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    .chatbot .message {
        font-size: 1.1rem;
        font-family: 'Shrikhand', cursive;
    }
    .chatbot .user,
    .chatbot .bot {
        background: #ffffff !important;
        color: #000000 !important;
        border-radius: 18px !important;
    }
    .chatbot .user * ,
    .chatbot .bot * {
        color: #000000 !important;
    }
"""

with gr.Blocks() as demo:
    gr.HTML('''<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Shrikhand&display=swap" rel="stylesheet">''')
    with gr.Column(elem_classes=["panel-wrap"]):
        gr.HTML('<div id="chat-title">your chatbot</div>')

        with gr.Column(elem_classes=["main-chat"]):
            chatbot = gr.Chatbot(height=420, elem_classes=["chatbot"])

        textbox = gr.Textbox(
            show_label=False,
            lines=2,
            placeholder="enter",
            elem_classes=["chat-input-wrap"],
        )

        with gr.Row(elem_classes=["action-row"]):
            submit = gr.Button("send", elem_classes=["action-button"])
            clear = gr.Button("clear", elem_classes=["action-button", "clear-button"])

    def respond(message, history):
        if not message or not message.strip():
            return history, ""
        reply = get_response(message, history)
        history = history or []
        formatted_history = []
        for item in history:
            if isinstance(item, dict):
                formatted_history.append(item)
            elif isinstance(item, tuple) and len(item) == 2:
                user_content, assistant_content = item
                if user_content:
                    formatted_history.append({"role": "user", "content": user_content})
                if assistant_content:
                    formatted_history.append({"role": "assistant", "content": assistant_content})
        formatted_history.append({"role": "user", "content": message})
        formatted_history.append({"role": "assistant", "content": reply})
        return formatted_history, ""

    submit.click(fn=respond, inputs=[textbox, chatbot], outputs=[chatbot, textbox])
    textbox.submit(fn=respond, inputs=[textbox, chatbot], outputs=[chatbot, textbox])
    clear.click(fn=lambda: ([], ""), inputs=None, outputs=[chatbot, textbox])

if __name__ == "__main__":
    preferred_port = int(os.getenv("GRADIO_SERVER_PORT", "7861"))
    try:
        demo.launch(debug=True, share=False, server_name="127.0.0.1", server_port=preferred_port, css=css)
    except OSError:
        fallback_port = preferred_port + 1
        print(f"Port {preferred_port} is busy. Retrying on {fallback_port}...")
        demo.launch(debug=True, share=False, server_name="127.0.0.1", server_port=fallback_port, css=css)
