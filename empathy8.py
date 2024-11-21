from flask import Flask, request, jsonify
import openai
import pyttsx3
import speech_recognition as sr
import random
import time
import os

# Set your OpenAI API Key from an environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize Flask app
app = Flask(__name__)

# Initialize speech recognizer and text-to-speech engine
recognizer = sr.Recognizer()
engine = pyttsx3.init()

# Filters for inappropriate content
FORBIDDEN_TOPICS = ["race", "religion", "nationality", "violence", "hate", "insult", "offensive"]

# Quit keywords
QUIT_KEYWORDS = ["goodbye", "exit", "leave", "quit", "bye"]

# Mapping of words to numbers for better age recognition
NUMBER_MAPPING = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
    "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
    "nineteen": 19, "twenty": 20
}

# Empathetic conversation topics with context keys
CONVERSATION_TOPICS = [
    {"prompt": "What do you love most about your day so far?", "context": "general"},
    {"prompt": "What's your favorite color? I bet it's a wonderful one!", "context": "color"},
    {"prompt": "Do you have a toy or something special that makes you happy?", "context": "toy"},
    {"prompt": "What shows or movies do you enjoy watching?", "context": "media"},
    {"prompt": "What’s a fun activity you like to do when you have free time?", "context": "activity"},
    {"prompt": "Do you have any pets? What do you love most about them?", "context": "pets"},
    {"prompt": "Who is someone you enjoy spending time with, and why?", "context": "relationships"},
    {"prompt": "What is your favorite food that makes you smile?", "context": "food"},
    {"prompt": "If you could play any game right now, what would it be?", "context": "games"}
]

# Variations for responses to avoid repetition
RESPONSE_VARIATIONS = {
    "general": ["That sounds amazing!", "That's so interesting!", "Wow, that must be so much fun!"],
    "color": ["What a beautiful color!", "Yellow is so cheerful and bright!", "That's such a lovely choice."],
    "toy": ["That sounds like a lot of fun!", "Toys like that can bring so much happiness!", "I bet that's really special to you."],
    "media": ["Oh, I love hearing about movies and shows!", "That sounds like a great choice.", "I bet that's a lot of fun to watch!"],
    "activity": ["That sounds exciting!", "What a great way to spend your time!", "I can see why you enjoy that."],
    "pets": ["Pets are so wonderful!", "They must bring you so much joy!", "I bet your pet is amazing."],
    "relationships": ["Spending time with loved ones is the best!", "What a great person to enjoy your time with!", "They must mean a lot to you."],
    "food": ["That sounds delicious!", "I love that food too!", "What a tasty choice!"],
    "games": ["Games are so much fun!", "What an exciting way to spend your time!", "I bet you're amazing at that game!"]
}

# Set the voice to Zira and max volume
def set_voice_to_zira():
    voices = engine.getProperty('voices')
    for voice in voices:
        if "zira" in voice.name.lower():
            engine.setProperty('voice', voice.id)
            print(f"Voice set to: {voice.name}")
            break
    engine.setProperty('volume', 1.0)  # Set volume to maximum
    print("Volume set to maximum.")

# Function to handle emotional responses with empathy
def handle_emotion_response(emotion):
    if "sad" in emotion.lower():
        return "I'm sorry to hear that you're feeling sad. Do you want to talk about what's making you feel this way?"
    elif "happy" in emotion.lower():
        return "That's wonderful to hear! I'm so glad you're feeling happy!"
    elif "angry" in emotion.lower():
        return "It's okay to feel angry sometimes. Would you like to tell me what's bothering you?"
    elif "excited" in emotion.lower():
        return "That's awesome! What are you excited about?"
    elif "nervous" in emotion.lower():
        return "Feeling nervous is normal. Do you want to share what's on your mind?"
    else:
        return f"Thanks for sharing how you're feeling. Let's talk more and see how I can help!"

# Function to check for inappropriate content
def filter_inappropriate_content(user_input):
    if not user_input:
        return False
    for topic in FORBIDDEN_TOPICS:
        if topic in user_input.lower():
            return True
    return False

# Function to check for quit keywords
def is_quit_command(user_input):
    if not user_input:
        return False
    for quit_word in QUIT_KEYWORDS:
        if quit_word in user_input.lower():
            return True
    return False

# Function to map spoken numbers to integers
def parse_age_input(age_input):
    if not age_input:
        return None
    try:
        words = age_input.lower().split()
        for word in words:
            if word in NUMBER_MAPPING:
                return NUMBER_MAPPING[word]
        return int(''.join(filter(str.isdigit, age_input)))
    except (ValueError, TypeError):
        return None

# Flask route for chatbot API
@app.route("/chat", methods=["POST"])
def chat():
    """Handle chatbot interactions via web API."""
    user_input = request.json.get("message", "")
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=user_input,
            max_tokens=150
        )
        reply = response["choices"][0]["text"].strip()
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Function to speak text and display it
def speak_and_display(text):
    print(f"Chatbot: {text}")
    engine.say(text)
    engine.runAndWait()
    time.sleep(0.3)  # Short delay for audio synchronization

# Main chatbot interaction function
def chatbot_interaction():
    """Handle interactive chatbot sessions with voice and text."""
    set_voice_to_zira()
    speak_and_display("Hi there! How are you today?")
    response = input("Child: ")  # Simulate user input for testing
    if is_quit_command(response):
        speak_and_display("Goodbye! It was so nice talking to you!")
        return
    speak_and_display("Let's continue chatting!")

if __name__ == "__main__":
    set_voice_to_zira()
    app.run(host="0.0.0.0", port=5000, debug=True)
