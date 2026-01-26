from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from openai import OpenAI
import os
from dotenv import load_dotenv

# -----------------------------
# ENV + OPENAI CONFIGURATION
# -----------------------------

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# -----------------------------
# FLASK APP SETUP
# -----------------------------

app = Flask(__name__)
CORS(app)

RASA_URL = "http://localhost:5005/webhooks/rest/webhook"

# -----------------------------
# SIMPLE CONTEXT MEMORY
# -----------------------------
# Stores ONLY learning context (never small talk)
conversation_context = {}

# -----------------------------
# LLM TEACHING FUNCTION
# -----------------------------

def simplify_with_llm(text, topic=None):
    topic_hint = ""
    if topic:
        topic_hint = (
            f"The current topic is: {topic}. "
            "Stay on this topic unless the child changes it.\n"
        )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are NEMO, a friendly learning buddy for a 6-year-old child with dyslexia.\n"
                        + topic_hint +
                        "Rules:\n"
                        "- Understand ANY question or sentence\n"
                        "- Use VERY simple words\n"
                        "- Short sentences\n"
                        "- Bullet points when helpful\n"
                        "- Be kind, encouraging, and calm\n"
                        "- Never say goodbye unless the child says bye\n"
                        "- If the topic changes, follow it naturally\n"
                    )
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            temperature=0.4,
            max_tokens=250
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("OPENAI ERROR:", e)
        return "😊 It’s okay. Let me explain it slowly."

# -----------------------------
# CHAT ENDPOINT
# -----------------------------

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)

    user_id = "default_user"  # demo user
    user_msg = data.get("message", "").strip()
    action = data.get("action")

    context = conversation_context.get(user_id)

    affirmations = ["yes", "yeah", "yep", "yup", "okay", "ok"]
    negations = ["no", "nope", "nah"]

    # -----------------------------
    # 🧠 HANDLE BUTTON ACTIONS
    # -----------------------------
    if action == "simpler" and context:
        simplified = simplify_with_llm(
            context["last_reply"],
            topic=context["last_topic"]
        )
        conversation_context[user_id]["last_reply"] = simplified
        return jsonify({"reply": simplified})

    if action == "explain_more" and context:
        expanded = simplify_with_llm(
            f"Explain more about {context['last_topic']}",
            topic=context["last_topic"]
        )
        conversation_context[user_id]["last_reply"] = expanded
        return jsonify({"reply": expanded})

    # -----------------------------
    # 🧠 HANDLE YES / NO CONTEXTUALLY
    # -----------------------------
    if user_msg.lower() in affirmations and context:
        reply = (
            "😊 Yay!\n"
            f"What would you like to know next about {context['last_topic']}?"
        )
        return jsonify({"reply": reply})

    if user_msg.lower() in negations and context:
        reply = (
            "That’s okay 😊\n"
            "You can ask me about something else anytime."
        )
        return jsonify({"reply": reply})

    # -----------------------------
    # 🧠 SMALL TALK → RASA
    # IMPORTANT: DO NOT SET last_topic HERE
    # -----------------------------
    small_talk = [
        "hi", "hello", "hey",
        "bye", "goodbye",
        "thanks", "thank you"
    ]

    if user_msg.lower() in small_talk:
        try:
            rasa_response = requests.post(
                RASA_URL,
                json={"sender": user_id, "message": user_msg},
                timeout=5
            ).json()
        except Exception as e:
            print("RASA error:", e)
            return jsonify({"reply": "😊 Hi! Let’s talk and learn together."})

        reply_text = None
        if isinstance(rasa_response, list):
            for item in rasa_response:
                if isinstance(item, dict) and "text" in item:
                    reply_text = item["text"]
                    break

        if reply_text:
            # ❌ DO NOT overwrite last_topic
            conversation_context[user_id] = {
                "last_reply": reply_text
            }
            return jsonify({"reply": reply_text})

    # -----------------------------
    # 🧠 DEFAULT: LEARNING MODE
    # -----------------------------
    # ANY meaningful input → teach with LLM

    topic = (
        context["last_topic"]
        if context and "last_topic" in context
        else user_msg
    )

    reply = simplify_with_llm(
        user_msg,
        topic=topic
    )

    # ✅ Store learning context ONLY here
    conversation_context[user_id] = {
        "last_topic": topic,
        "last_reply": reply
    }

    return jsonify({"reply": reply})

# -----------------------------
# RUN SERVER
# -----------------------------

if __name__ == "__main__":
    app.run(port=5000, debug=True)
# To run the app: python backend/app.py