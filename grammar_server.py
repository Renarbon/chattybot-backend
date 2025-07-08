from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os

app = Flask(__name__)
CORS(app)

import os
openai.api_key = os.environ.get("OPENAI_API_KEY")
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
@app.route("/api/check-key")
def check_key():
    import openai
    return jsonify({"key_present": bool(openai.api_key)})
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
