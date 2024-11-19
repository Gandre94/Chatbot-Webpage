from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import pyttsx3
import speech_recognition as sr
import os

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize text-to-speech engine
engine = pyttsx3.init()

def speak_text(text):
    """Use pyttsx3 to speak a given text."""
    engine.say(text)
    engine.runAndWait()

def listen_to_voice():
    """Capture user voice input and convert to text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for your input...")
        try:
            # Listen for audio and convert it to text
            audio = recognizer.listen(source, timeout=10)
            user_input = recognizer.recognize_google(audio)
            print(f"You said: {user_input}")
            return user_input
        except sr.UnknownValueError:
            print("Sorry, I could not understand your speech. Please try again.")
            return "Sorry, I could not understand your speech."
        except sr.RequestError as e:
            print(f"Error with the speech recognition service: {e}")
            return "Error with the speech recognition service."

@app.route('/chat', methods=['POST'])
def chat():
    # Handle text-based messages from the frontend
    data = request.get_json()
    user_message = data.get("message", "")

    try:
        # Generate a response using OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}]
        )
        reply = response['choices'][0]['message']['content']

        # Speak the reply
        speak_text(reply)

        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/voice', methods=['GET'])
def voice():
    # Handle voice input and provide a response
    try:
        user_message = listen_to_voice()
        if "Sorry" in user_message:  # If there was an error, return it
            return jsonify({"reply": user_message})

        # Generate a response using OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}]
        )
        reply = response['choices'][0]['message']['content']

        # Speak the reply
        speak_text(reply)

        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
