# grammar_server.py (updated backend with ElevenLabs TTS support)

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import openai
import os
import requests
from io import BytesIO

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")

elevenlabs_api_key = os.getenv("ELEVEN_API_KEY")

@app.route("/api/grammar-correct", methods=["POST"])
def correct_grammar():
    data = request.get_json()
    prompt = f"Correct the grammar of this sentence: {data['text']}"

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful English teacher."},
                {"role": "user", "content": prompt}
            ]
        )
        corrected = response['choices'][0]['message']['content']
        return jsonify({"corrected": corrected})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/tts", methods=["POST"])
def tts():
    data = request.get_json()
    text = data.get("text")
    voice_id = data.get("voice_id", "3kmhLabcqbsGhEd3mEhD")

    headers = {
        "xi-api-key": elevenlabs_api_key,
        "Content-Type": "application/json"
    }

    payload = {
        "text": text
    }

    tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}?output_format=mp3_22050_32"
    response = requests.post(tts_url, headers=headers, json=payload)

    if response.status_code == 200:
        return send_file(BytesIO(response.content), mimetype='audio/mpeg')
    else:
        return jsonify({"error": "TTS request failed", "details": response.text}), 500


if __name__ == "__main__":
    app.run(debug=True)
