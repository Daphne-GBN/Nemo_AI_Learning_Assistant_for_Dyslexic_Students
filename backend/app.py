from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

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
            "If the child asks about something else, switch to the new topic.\n"
        )

    prompt = (
        "You are NEMO, a friendly learning buddy for a 6-year-old child with dyslexia.\n"
        + topic_hint +
        "Rules:\n"
        "- Understand ANY question or sentence\n"
        "- Use VERY simple words\n"
        "- Short sentences\n"
        "- Bullet points when helpful\n"
        "- Be kind, encouraging, and calm\n"
        "- Never say goodbye unless the child says bye\n"
        "- If the topic changes, follow it naturally\n\n"
        f"Child says: {text}\n"
        "NEMO replies:"
    )

    try:
        res = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "temperature": 0.4,
                "num_predict": 250,
                "stream": False
            },
            timeout=60
        )

        return res.json()["response"].strip()

    except Exception as e:
        print("OLLAMA ERROR:", e)
        return "It is okay. Let me explain it slowly."


def simplify_more_with_llm(text, topic=None):
    topic_hint = ""
    if topic:
        topic_hint = (
            f"The current topic is: {topic}. "
            "If the child asks about something else, switch to the new topic.\n"
        )

    prompt = (
        "You are NEMO, a friendly learning buddy for a 6-year-old child with dyslexia.\n"
        + topic_hint +
        "Task: Make the message MUCH simpler and shorter.\n"
        "Rules:\n"
        "- Use the simplest possible words\n"
        "- Max 2 short sentences OR 3 bullet points\n"
        "- Remove extra details and examples\n"
        "- Avoid metaphors unless necessary\n"
        "- Be kind and calm\n\n"
        f"Message to simplify: {text}\n"
        "NEMO replies:"
    )

    try:
        res = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "temperature": 0.3,
                "num_predict": 120,
                "stream": False
            },
            timeout=60
        )

        return res.json()["response"].strip()

    except Exception as e:
        print("OLLAMA ERROR:", e)
        return "It is okay. Here is a shorter, simpler answer."

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
    # HANDLE BUTTON ACTIONS
    # -----------------------------
    if action == "simpler" and context:
        simplified = simplify_more_with_llm(
            context.get("last_reply", ""),
            topic=context.get("last_topic")
        )
        conversation_context[user_id]["last_reply"] = simplified
        return jsonify({"reply": simplified})

    if action == "explain_more" and context:
        topic = context.get("last_topic") or "this topic"
        expanded = simplify_with_llm(
            f"Explain more about {topic}",
            topic=context.get("last_topic")
        )
        conversation_context[user_id]["last_reply"] = expanded
        return jsonify({"reply": expanded})

    # -----------------------------
    # HANDLE YES / NO CONTEXTUALLY
    # -----------------------------
    if user_msg.lower() in affirmations and context:
        reply = (
            "Yay!\n"
            f"What would you like to know next about {context['last_topic']}?"
        )
        return jsonify({"reply": reply})

    if user_msg.lower() in negations and context:
        reply = (
            "That is okay.\n"
            "You can ask me about something else anytime."
        )
        return jsonify({"reply": reply})

    # -----------------------------
    # SMALL TALK -> RASA
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
            return jsonify({"reply": "Hi! Let's talk and learn together."})

        reply_text = None
        if isinstance(rasa_response, list):
            for item in rasa_response:
                if isinstance(item, dict) and "text" in item:
                    reply_text = item["text"]
                    break

        if reply_text:
            # DO NOT overwrite last_topic
            conversation_context[user_id] = {
                "last_reply": reply_text
            }
            return jsonify({"reply": reply_text})

    # -----------------------------
    # DEFAULT: LEARNING MODE
    # -----------------------------
    # ANY meaningful input -> teach with LLM

    topic = None
    if context and "last_topic" in context:
        looks_like_new_topic = (
            len(user_msg.split()) >= 3
            and user_msg.lower() not in affirmations
            and user_msg.lower() not in negations
            and user_msg.lower() not in small_talk
        )
        topic = user_msg if looks_like_new_topic else context["last_topic"]
    else:
        topic = user_msg

    reply = simplify_with_llm(
        user_msg,
        topic=topic
    )

    # Store learning context ONLY here
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
