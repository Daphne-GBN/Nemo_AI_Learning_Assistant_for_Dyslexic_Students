from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests


class ActionTeachWithOllama(Action):

    def name(self) -> Text:
        return "action_teach_with_ollama"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        user_message = tracker.latest_message.get("text")

        prompt = f"""
You are NEMO, a friendly learning buddy for a child with dyslexia.

Rules:
- Use very simple words
- Use short sentences
- Explain in 3–4 lines only
- Use one small example

Question:
{user_message}

Answer:
"""

        try:
            res = requests.post(
                "http://127.0.0.1:11434/api/generate",
                json={
                    "model": "llama3",
                    "prompt": prompt,
                    "num_predict": 80,
                    "temperature": 0.4,
                    "stream": False
                },
                timeout=240
            )

            print("OLLAMA STATUS:", res.status_code)
            print("OLLAMA RAW RESPONSE:", res.text)

            reply = res.json().get("response", "").strip()

            if not reply:
                raise ValueError("Empty response from Ollama")

        except Exception as e:
            print("OLLAMA ERROR:", e)
            reply = "😊 It’s okay. Let me explain it slowly."

        dispatcher.utter_message(text=reply)
        return []

##✅ Correct way to run actions server

#From inside the Rasa project folder:

#cd D:\DP_prog\rasa
#rasa run actions


#You should see:

#Action server is up and running


#✅ That means rasa_sdk is working.

#🧪 Full correct run order (bookmark this)
#Terminal 1 (Ollama)
#ollama run llama3

#Terminal 2 (Actions)
#cd D:\DP_prog\rasa
#rasa run actions

#Terminal 3 (Rasa server)
#cd D:\DP_prog\rasa
#rasa run --enable-api --cors "*"

#Terminal 4 (Test)
#rasa shell
#rasa_env/Scripts/activate

