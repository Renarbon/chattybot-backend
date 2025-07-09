from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os

app = Flask(__name__)
CORS(app)

openai.api_key = os.environ.get("OPENAI_API_KEY")
LEMONFOX_API_KEY = os.environ.get("LEMONFOX_API_KEY")  # Set in your environment variables
@app.route("/api/grammar-correct", methods=["POST"])
def correct_grammar():
    try:
        data = request.get_json()
        text = data.get("text", "")
        if not text:
            return jsonify({"error": "No text provided"}), 400
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful English grammar corrector. Correct grammar and punctuation, but do not explain."},
                {"role": "user", "content": text}
            ],
            max_tokens=100,
            temperature=0.0,
        )
        corrected = response.choices[0].message.content.strip()
        return jsonify({"corrected": corrected})
    except Exception as e:
        print("Error in grammar-correct:", e)
        return jsonify({"error": str(e)}), 500

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

@app.route("/api/check-key")
def check_key():
    return jsonify({"key_present": bool(openai.api_key)})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
