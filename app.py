from flask import Flask, request, jsonify, render_template
import openai
import os
import base64
from TTS.api import TTS
import soundfile as sf
import io
import speech_recognition as sr

# Set your OpenAI API Key from an environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set.")

# Initialize Flask app
app = Flask(__name__)

# Initialize Coqui TTS
tts = TTS(model_name="tts_models/en/ljspeech/vits--neon", progress_bar=False, gpu=False)

# Initialize speech recognizer
recognizer = sr.Recognizer()

# Filters for inappropriate content
FORBIDDEN_TOPICS = ["race", "religion", "nationality", "violence", "hate", "insult", "offensive"]
QUIT_KEYWORDS = ["goodbye", "exit", "leave", "quit", "bye"]

# Function to filter inappropriate content
def filter_inappropriate_content(user_input):
    if not user_input:
        return False
    for topic in FORBIDDEN_TOPICS:
        if topic in user_input.lower():
            return True
    return False

# Function to recognize quit commands
def is_quit_command(user_input):
    if not user_input:
        return False
    for quit_word in QUIT_KEYWORDS:
        if quit_word in user_input.lower():
            return True
    return False

# Function to generate chatbot response using OpenAI's API
def generate_response(user_input, conversation_history):
    try:
        if not user_input:
            return "I didn't catch that. Could you say it again?", False
        if filter_inappropriate_content(user_input):
            return "Let's keep our conversation kind and positive.", False
        if is_quit_command(user_input):
            return "Goodbye! It was so nice talking to you!", True

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful chatbot."},
                {"role": "user", "content": user_input},
            ]
        )

        chatbot_response = response['choices'][0]['message']['content'].strip()
        conversation_history.append({"user": user_input, "assistant": chatbot_response})
        return chatbot_response, False

    except Exception as e:
        return f"An error occurred: {str(e)}", False

# Function to process empathy data
def process_empathy(data):
    message = data.get("message", "")
    empathetic_response = f"I understand that you're feeling: {message}. It's important to acknowledge these emotions."
    return {"response": empathetic_response}

# Route for the main page
@app.route("/")
def home():
    return render_template("index.html")

# Route for handling chat messages
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_input = data.get("message", "")
        conversation_history = data.get("history", [])

        # Process empathy if a key exists in the data
        if "empathy" in data:
            empathy_response = process_empathy(data)
            return jsonify(empathy_response)

        # Generate chatbot response
        response, quit_flag = generate_response(user_input, conversation_history)

        # Convert response to speech using Coqui TTS
        audio_data = tts.tts(response)
        audio_buffer = io.BytesIO()
        sf.write(audio_buffer, audio_data, samplerate=tts.synthesizer.output_sample_rate, format='WAV')
        audio_buffer.seek(0)
        audio_bytes = audio_buffer.read()
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')

        return jsonify({"reply": response, "history": conversation_history, "quit": quit_flag, "audio": audio_base64})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Entry point for the application
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
