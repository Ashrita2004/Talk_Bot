from flask import Flask, render_template, request, jsonify
import wikipedia
import json
import os
import waitress

app = Flask(__name__)

CHAT_HISTORY_FILE = "chat_history.json"

# Ensure the chat history file exists
if not os.path.exists(CHAT_HISTORY_FILE):
    with open(CHAT_HISTORY_FILE, "w") as file:
        json.dump([], file)

# Friendly predefined responses
predefined_responses = {
    "hello talkbot": "Hello! how can I assist you today?",
    "thank you" : "You're very welcome! 😊 I'm glad I could help.",
    "who are you?": "Hey there! I'm TalkBot, your friendly AI assistant. 😊",
    "are you a bot?": "Yep! I'm a smart chatbot, always here to help. 🤖",
    "what is your name?": "I'm TalkBot! What's yours? 😃",
    "bye": "Goodbye! Hope to chat with you again soon! 👋",
    "goodbye": "See you later! Take care! 😊"
}

def load_chat_history():
    """Load chat history from file if exists."""
    try:
        with open(CHAT_HISTORY_FILE, "r") as file:
            return json.load(file)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_chat_history(history):
    """Save chat history to file."""
    with open(CHAT_HISTORY_FILE, "w") as file:
        json.dump(history, file, indent=4)

def get_wikipedia_summary(query):
    """Fetch a short and friendly Wikipedia summary."""
    try:
        summary = wikipedia.summary(query, sentences=2)
        return f"Here's what I found: {summary} 😊"
    except wikipedia.exceptions.DisambiguationError as e:
        return f"That topic is a bit broad! Did you mean: {', '.join(e.options[:5])}? 🤔"
    except wikipedia.exceptions.PageError:
        return "Oops! I couldn't find anything on that topic. Maybe try another question? 🤷‍♂️"
    except Exception:
        return "Uh-oh! I ran into a little trouble looking that up. Try again later! 😅"

@app.route("/")
def index():
    """Render the chat page."""
    return render_template('chat.html')

@app.route("/get", methods=["POST"])
def chat():
    """Handles user input and generates a response."""
    user_input = request.form["msg"].strip().lower()

    # Load chat history
    chat_history = load_chat_history()

    # Append user input to chat history
    chat_history.append({"user": user_input})

    # Check predefined responses first
    if user_input in predefined_responses:
        bot_response = predefined_responses[user_input]
    else:
        # Fetch Wikipedia response
        bot_response = get_wikipedia_summary(user_input)

    # Append bot response to chat history
    chat_history.append({"bot": bot_response})

    # Save updated chat history
    save_chat_history(chat_history)

    return jsonify(bot_response)

@app.route("/clear", methods=["GET"])
def clear_history():
    """Clear chat history."""
    save_chat_history([])  # Overwrite with an empty list
    return jsonify({"message": "Chat history cleared!"})

if __name__ == "__main__":
    print("🚀 Starting TalkBot server using Waitress on http://127.0.0.1:5000")
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)

