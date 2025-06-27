import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import traceback

app = Flask(__name__)
CORS(app)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = openai.OpenAI(api_key=OPENAI_API_KEY)

@app.route("/api/grammar-correct", methods=["POST"])
def correct_grammar():
    data = request.get_json()
    text = data.get("text", "")

    prompt = (
        "You are an English teacher. Please analyze the student's spoken answer below. "
        "1. Give a brief feedback on their grammar (1-2 sentences). "
        "2. Then rewrite their answer in perfect English (as you would say it). "
        "Format your answer as:\n\nFeedback: ...\nCorrection: ...\n\n"
        f"Student's answer: {text}"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful English teacher."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.2
        )
        reply = response.choices[0].message.content.strip()
        feedback, correction = "", ""
        for line in reply.splitlines():
            if line.lower().startswith("feedback:"):
                feedback = line[9:].strip()
            if line.lower().startswith("correction:"):
                correction = line[11:].strip()
        if not feedback or not correction:
            feedback = reply
            correction = ""
        return jsonify({"feedback": feedback, "correction": correction})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"feedback": "API error.", "correction": "", "error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


