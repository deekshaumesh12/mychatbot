import os

import gradio as gr
from dotenv import load_dotenv

load_dotenv()

# This app no longer calls an external API. It uses a simple local responder
# to make the UI work offline and avoid exposing API keys.
model_name = os.getenv("MODEL", "local-demo")
max_tokens = int(os.getenv("MAX_TOKENS", "256"))


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


def local_response_logic(message, history):
    # Very small local logic for demo purposes.
    text = message.strip()
    if not text:
        return ""
    lower = text.lower()
    if "hello" in lower or "hi" in lower:
        return "Hi there — this is a local Gradio demo (no external API)."
    if "help" in lower:
        return "Try typing a question or 'hello'. This is a local demo responder."
    # otherwise echo back a concise acknowledgment
    return f"(local) I received your message: {text}"


def get_response(message, history):
    if not message or not message.strip():
        return ""
    try:
        return local_response_logic(message, history)
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
    # Runtime settings (adjust here or via environment variables)
    GRADIO_SERVER_PORT = int(os.getenv("GRADIO_SERVER_PORT", "7861"))
    GRADIO_SERVER_NAME = os.getenv("GRADIO_SERVER_NAME", "127.0.0.1")
    GRADIO_DEBUG = os.getenv("DEBUG", "1") in {"1", "true", "True"}

    try:
        demo.launch(
            debug=GRADIO_DEBUG,
            share=False,
            server_name=GRADIO_SERVER_NAME,
            server_port=GRADIO_SERVER_PORT,
            css=css,
        )
    except OSError:
        fallback_port = GRADIO_SERVER_PORT + 1
        print(f"Port {GRADIO_SERVER_PORT} is busy. Retrying on {fallback_port}...")
        demo.launch(
            debug=GRADIO_DEBUG,
            share=False,
            server_name=GRADIO_SERVER_NAME,
            server_port=fallback_port,
            css=css,
        )
