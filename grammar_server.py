from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import openai
import os
import requests

app = Flask(__name__)
# Configure CORS to allow all origins for API endpoints
# NOTE: If you need to restrict origins in production, replace "*" with specific domains:
# CORS(app, resources={r"/api/*": {"origins": ["https://yourdomain.com"], ...}})
CORS(app, resources={r"/api/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"], "allow_headers": ["Content-Type", "Authorization"]}})

# Set your OpenAI API key via environment variable or here directly (not recommended)
openai.api_key = os.environ.get("OPENAI_API_KEY")
LEMONFOX_API_KEY = os.environ.get("LEMONFOX_API_KEY")  # Lemonfox TTS key

# === Chatbot Endpoint ===
@app.route('/api/chatbot', methods=['POST'])
def chatbot():
    data = request.get_json()
    message = data.get('message', '')
    if not message:
        return jsonify({'error': 'No message provided'}), 400

    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message}]
        )
        response_content = completion.choices[0].message['content'].strip()
        return jsonify({'response': response_content})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# === Grammar Correction Endpoint ===
@app.route('/api/grammar-correct', methods=['POST'])
def grammar_correct():
    data = request.get_json()
    text = data.get('text', '')
    if not text:
        return jsonify({'error': 'No text provided'}), 400

    prompt = (
        "Analyze the following English text for grammar mistakes. "
        "First, provide a short FEEDBACK summary explaining any typical errors or issues found (if any). "
        "Second, give a SUGGESTED CORRECTION with improved grammar. "
        "Reply in JSON format with keys 'feedback' and 'correction'.\n\n"
        f"{text}"
    )
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        import json
        response_content = completion.choices[0].message['content'].strip()
        # Try to parse GPT output as JSON
        try:
            result = json.loads(response_content)
            feedback = result.get("feedback", "")
            correction = result.get("correction", "")
        except Exception:
            # Fallback: if GPT does not return JSON, treat the whole output as correction
            feedback = ""
            correction = response_content

        return jsonify({'feedback': feedback, 'correction': correction})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# === Lemonfox TTS Proxy Endpoint ===
@app.route('/api/lemonfox-tts', methods=['POST'])
def lemonfox_tts():
    data = request.get_json()
    print("Received data:", data)
    # Accept both "text" and "input" for flexibility (frontends may vary)
    text = data.get('text') or data.get('input', '')
    voice = data.get('voice', 'en-US-AndyNeural')
    if not text:
        print("No text provided.")
        return "No text provided", 400
    response = requests.post(
        "https://api.lemonfox.ai/v1/audio/speech",
        headers={"Authorization": f"Bearer {LEMONFOX_API_KEY}",
                 "Content-Type": "application/json"},
        json={
            "input": text,
            "voice": voice,
            "response_format": "mp3"
        }
    )
    print("Lemonfox status:", response.status_code)
    print("Lemonfox response:", response.text[:500])  # Print first 500 chars for debugging
    if not response.ok:
        return ("Lemonfox error: " + response.text, 400)
    return Response(response.content, mimetype="audio/mpeg")

# === ElevenLabs TTS Endpoint (NEW!) ===
@app.route('/api/tts', methods=['POST'])
def elevenlabs_tts():
    text = request.get_json().get('text', '')
    if not text:
        return "No text provided", 400
    ELEVENLABS_API_KEY = os.environ.get("ELEVEN_API_KEY")  # Use your actual env var name!
    VOICE_ID = "ds0uumbpvplhO4tyz2yF"  # Your chosen ElevenLabs voice
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/stream"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "model_id": "eleven_turbo_v2",  # Use "eleven_turbo_v2" or your preferred model
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }
    response = requests.post(url, headers=headers, json=payload, stream=True)
    if not response.ok:
        return ("ElevenLabs error: " + response.text, 400)
    return Response(response.content, mimetype="audio/mpeg")

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

