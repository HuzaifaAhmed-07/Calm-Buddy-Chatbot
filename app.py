import gradio as gr
import os
import requests

# API CONFIG 
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_NAME = "llama-3.1-8b-instant"

#  GROQ QUERY 
def query_groq(message, chat_history, support_type):
    if not GROQ_API_KEY:
        return "⚠️ Please add your GROQ_API_KEY in Hugging Face Spaces → Settings → Secrets."

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    system_message = """You are CalmBuddy, a gentle, supportive, and non-judgmental stress relief companion. Your goal is to help users feel calmer during moments of stress or anxiety. You provide emotional reassurance, simple breathing exercises, grounding techniques, and gentle encouragement. You do not give medical advice or diagnoses. You keep responses calm, warm, short, and easy to follow. You focus on helping the user feel better in the present moment."""

    messages = [{"role": "system", "content": system_message}]

    for user_msg, bot_msg in chat_history:
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": bot_msg})

    enhanced_message = f"Support style requested: {support_type}. User message: {message}"
    messages.append({"role": "user", "content": enhanced_message})

    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": 0.4
    }

    response = requests.post(GROQ_API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"Error {response.status_code}: {response.text}"

#  CHAT HANDLER 
def respond(message, chat_history, support_type):
    bot_reply = query_groq(message, chat_history, support_type)
    chat_history.append((message, bot_reply))
    return "", chat_history

# QUICK RELIEF BUTTONS 
def breathing_exercise(chat_history):
    exercise = (
        "Let’s slow things down together 🌿\n\n"
        "• Inhale slowly for 4 seconds\n"
        "• Hold for 4 seconds\n"
        "• Exhale gently for 6 seconds\n\n"
        "Repeat this 5 times. You’re safe right now."
    )
    chat_history.append(("Breathing Exercise", exercise))
    return chat_history

def grounding_exercise(chat_history):
    exercise = (
        "Let’s ground you in the present 🌱\n\n"
        "Name:\n"
        "• 5 things you can see\n"
        "• 4 things you can feel\n"
        "• 3 things you can hear\n"
        "• 2 things you can smell\n"
        "• 1 thing you can taste\n\n"
        "Take your time."
    )
    chat_history.append(("Grounding Exercise", exercise))
    return chat_history

#  RESET 
def reset_chat():
    return []

#  UI 
with gr.Blocks(theme=gr.themes.Soft(primary_hue="blue", secondary_hue="green")) as demo:
    gr.Markdown("## 🧘 Calm Buddy")
    gr.Markdown("### Your gentle companion for stress relief and emotional grounding")

    chatbot = gr.Chatbot(height=420)

    with gr.Row():
        support_type = gr.Dropdown(
            choices=[
                "Emotional Support",
                "Breathing Guidance",
                "Grounding Techniques",
                "Motivational Encouragement"
            ],
            value="Emotional Support",
            label="What kind of support do you need?"
        )

    msg = gr.Textbox(
        label="How are you feeling right now?",
        placeholder="e.g., I feel overwhelmed and anxious about everything"
    )

    with gr.Row():
        breathe_btn = gr.Button("🌬️ Breathing Exercise")
        ground_btn = gr.Button("🌱 Grounding Exercise")
        reset_btn = gr.Button("🔄 Reset Chat")

    state = gr.State([])

    msg.submit(respond, [msg, state, support_type], [msg, chatbot])
    breathe_btn.click(breathing_exercise, [state], chatbot)
    ground_btn.click(grounding_exercise, [state], chatbot)
    reset_btn.click(reset_chat, outputs=chatbot)

demo.launch()
