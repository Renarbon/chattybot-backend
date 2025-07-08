# grammar_server.py (updated backend with ElevenLabs TTS support)

from flask import Flask, request, jsonify
from flask_cors import CORS
import openai

app = Flask(__name__)
CORS(app)

OPENAI_API_KEY = "sk-YOUR_OPENAI_API_KEY"  # Your real key (do NOT put in frontend)

openai.api_key = OPENAI_API_KEY

# ...your grammar route here...

@app.route("/api/chatbot", methods=["POST"])
def chatbot_reply():
    try:
        data = request.get_json()
        messages = data.get("messages", [])
        model = data.get("model", "gpt-4o")

        response = openai.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=150,
            temperature=0.7,
        )
        bot_reply = response.choices[0].message.content
        return jsonify({"reply": bot_reply})
    except Exception as e:
        print("Error in chatbot:", e)
        return jsonify({"reply": "Sorry, I couldn't connect to the server."}), 500

# ...your other routes...



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

