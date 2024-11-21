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

# Mapping spoken numbers to integers for age recognition
NUMBER_MAPPING = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
    "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
    "nineteen": 19, "twenty": 20
}

# Empathetic conversation topics
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
            engine.setProperty('voice", voice.id)
            print(f"Voice set to: {voice.name}")
            break
    engine.setProperty('volume', 1.0)  # Set volume to maximum
    print("Volume set to maximum.")

# Function to handle empathetic responses
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

# Flask route for chatbot API (for web mode)
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

# Function to listen to user input via microphone
def get_audio_input(prompt):
    """Capture user input via speech recognition."""
    speak_and_display(prompt)
    with sr.Microphone() as source:
        try:
            print("Listening...")
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=8)
            recognized_text = recognizer.recognize_google(audio)
            print(f"Child: {recognized_text}")
            return recognized_text
        except sr.UnknownValueError:
            speak_and_display("I'm sorry, I didn't catch that. Could you try again?")
            return None
        except sr.WaitTimeoutError:
            speak_and_display("I didn't hear anything. Could you try again?")
            return None
        except sr.RequestError as e:
            speak_and_display("I'm sorry, there seems to be a problem with the microphone.")
            return None

# Interactive mode: Voice-based interaction only
def interactive_chat():
    """Handle interactive chatbot sessions with voice and record conversation."""
    set_voice_to_zira()
    conversation_log = []

    speak_and_display("Hi there! How are you today?")
    while True:
        user_input = get_audio_input("Please tell me more:")
        if not user_input:
            continue
        if is_quit_command(user_input):
            speak_and_display("Goodbye! It was so nice talking to you!")
            break
        if filter_inappropriate_content(user_input):
            speak_and_display("Let's keep our conversation kind and positive.")
            continue
        response = handle_emotion_response(user_input)
        speak_and_display(response)

        # Log conversation
        conversation_log.append({"user": user_input, "ai": response})

    # Save conversation log to a file
    with open("conversation_log.txt", "w") as log_file:
        for entry in conversation_log:
            log_file.write(f"User: {entry['user']}\n")
            log_file.write(f"AI: {entry['ai']}\n\n")

if __name__ == "__main__":
    interactive_chat()
