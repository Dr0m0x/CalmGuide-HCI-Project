"""
CalmGuide - An AI-Based Adaptive Wellness Chatbot
HCI Project: AI-Based Adaptive Human-Computer Interaction

This Flask application implements an adaptive chatbot that modifies its
responses based on tracked user interaction history (session memory),
sentiment/keyword detection, and recommendation generation.

Adaptive logic overview:
- Tracks counts of stress-related, educational, and positive messages per session.
- When stress-related messages cross a threshold, the bot proactively
  prioritizes calming/breathing exercises.
- When educational questions cross a threshold, the bot switches to a
  more detailed informational response style.
- Positive interactions generate encouraging follow-up messages.
- All session data is stored temporarily in memory (per-session dict) and
  is never persisted to disk, addressing privacy considerations.
"""

from flask import Flask, render_template, request, jsonify, session
import re
import uuid
import random

app = Flask(__name__)
app.secret_key = "calmguide-dev-secret-key"  # for session cookie signing

# ---------------------------------------------------------------------------
# In-memory session store
# Structure: { session_id: {"stress_count": int, "edu_count": int,
#                            "positive_count": int, "history": []} }
# ---------------------------------------------------------------------------
SESSION_STORE = {}

STRESS_THRESHOLD = 2
EDU_THRESHOLD = 2

# ---------------------------------------------------------------------------
# Keyword dictionaries used for simple rule-based intent / sentiment detection
# ---------------------------------------------------------------------------
STRESS_KEYWORDS = [
    "stress", "stressed", "anxious", "anxiety", "overwhelmed",
    "worried", "worry", "panic", "nervous", "tense", "burnout",
    "can't sleep", "cant sleep", "scared", "afraid"
]

EDUCATIONAL_KEYWORDS = [
    "what is", "how does", "explain", "why does", "tell me about",
    "what are", "how do", "define", "information about", "learn about"
]

POSITIVE_KEYWORDS = [
    "thanks", "thank you", "great", "feeling better", "helped",
    "good", "awesome", "happy", "appreciate", "better now", "calm now"
]

BREATHING_EXERCISES = [
    "Let's try a quick breathing exercise: breathe in for 4 seconds, "
    "hold for 4 seconds, and exhale slowly for 6 seconds. Repeat this "
    "three times.",
    "Try the 5-5-5 technique: inhale for 5 seconds, hold for 5 seconds, "
    "and release for 5 seconds. Focus only on your breath as you do this.",
    "Here's a grounding exercise: name 5 things you can see, 4 things you "
    "can touch, 3 things you can hear, 2 things you can smell, and 1 thing "
    "you can taste."
]

EDUCATIONAL_RESOURCES = {
    "stress": "Stress is the body's natural response to demands or "
              "threats, triggering the release of hormones like cortisol "
              "and adrenaline. Chronic stress can affect sleep, mood, and "
              "physical health, but techniques such as deep breathing, "
              "exercise, and mindfulness can help regulate the stress "
              "response.",
    "anxiety": "Anxiety is a feeling of worry, nervousness, or unease, "
               "often about something with an uncertain outcome. While "
               "occasional anxiety is normal, persistent anxiety may "
               "benefit from coping strategies like grounding exercises, "
               "journaling, or speaking with a mental health professional.",
    "mindfulness": "Mindfulness is the practice of focusing your "
                   "attention on the present moment without judgment. "
                   "Research suggests regular mindfulness practice can "
                   "reduce stress, improve focus, and support emotional "
                   "regulation.",
    "default": "Wellness involves a balance of mental, emotional, and "
               "physical health. Small daily habits such as adequate "
               "sleep, hydration, movement, and moments of reflection can "
               "have a meaningful cumulative effect on overall wellbeing."
}

GENERIC_RESPONSES = [
    "I'm here to help with your wellness journey. Could you tell me more "
    "about how you're feeling?",
    "Thanks for sharing that with me. What's on your mind today?",
    "I'm listening. Feel free to share what's been going on."
]


def detect_intent(message):
    """Return a tuple of booleans (is_stress, is_educational, is_positive)
    based on simple keyword matching against the lowercase message."""
    text = message.lower()
    is_stress = any(kw in text for kw in STRESS_KEYWORDS)
    is_educational = any(kw in text for kw in EDUCATIONAL_KEYWORDS)
    is_positive = any(kw in text for kw in POSITIVE_KEYWORDS)
    return is_stress, is_educational, is_positive


def get_educational_topic(message):
    """Identify which educational resource best matches the message."""
    text = message.lower()
    for topic in EDUCATIONAL_RESOURCES:
        if topic != "default" and topic in text:
            return topic
    return "default"


def get_session_data():
    """Retrieve or initialize this user's session data."""
    if "sid" not in session:
        session["sid"] = str(uuid.uuid4())

    sid = session["sid"]
    if sid not in SESSION_STORE:
        SESSION_STORE[sid] = {
            "stress_count": 0,
            "edu_count": 0,
            "positive_count": 0,
            "history": []
        }
    return SESSION_STORE[sid]


def build_response(message, data):
    """
    Core adaptive logic. Determines intent, updates session counters,
    and selects a response strategy based on accumulated history.
    """
    is_stress, is_educational, is_positive = detect_intent(message)

    if is_stress:
        data["stress_count"] += 1
    if is_educational:
        data["edu_count"] += 1
    if is_positive:
        data["positive_count"] += 1

    # --- Adaptive branch 1: repeated stress signals -> prioritize calming ---
    if data["stress_count"] >= STRESS_THRESHOLD:
        exercise = random.choice(BREATHING_EXERCISES)
        if is_stress:
            response = (
                "I've noticed you've mentioned feeling stressed or anxious "
                "more than once. Let's focus on a calming exercise right "
                "now. " + exercise
            )
        else:
            response = (
                "Before we continue, since you've been feeling stressed "
                "lately, here's a quick calming exercise: " + exercise
            )
        adaptation_note = "stress_priority_mode"

    # --- Adaptive branch 2: stress mentioned once -> immediate support ---
    elif is_stress:
        exercise = random.choice(BREATHING_EXERCISES)
        response = (
            "It sounds like you might be feeling some stress. " + exercise +
            " Would you like to talk more about what's causing it?"
        )
        adaptation_note = "single_stress_response"

    # --- Adaptive branch 3: repeated educational questions -> detailed mode
    elif data["edu_count"] >= EDU_THRESHOLD and is_educational:
        topic = get_educational_topic(message)
        resource = EDUCATIONAL_RESOURCES.get(topic, EDUCATIONAL_RESOURCES["default"])
        response = (
            "Since you're interested in learning more, here's a more "
            "detailed explanation: " + resource +
            " Let me know if you'd like to dive deeper into any part of this."
        )
        adaptation_note = "detailed_education_mode"

    # --- Adaptive branch 4: educational question (first/second time) ---
    elif is_educational:
        topic = get_educational_topic(message)
        resource = EDUCATIONAL_RESOURCES.get(topic, EDUCATIONAL_RESOURCES["default"])
        response = resource
        adaptation_note = "standard_education_response"

    # --- Adaptive branch 5: positive sentiment -> encouragement ---
    elif is_positive:
        response = (
            "I'm really glad to hear that! Keep up whatever is working "
            "for you. Is there anything else you'd like support with today?"
        )
        adaptation_note = "positive_encouragement"

    # --- Default branch ---
    else:
        response = random.choice(GENERIC_RESPONSES)
        adaptation_note = "generic_response"

    # Record this exchange in history (used for transparency / debugging)
    data["history"].append({
        "user": message,
        "bot": response,
        "adaptation": adaptation_note,
        "stress_count": data["stress_count"],
        "edu_count": data["edu_count"],
        "positive_count": data["positive_count"]
    })

    return response, adaptation_note


@app.route("/")
def index():
    """Render the main chat interface."""
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    """Handle an incoming chat message and return the adaptive response."""
    payload = request.get_json(silent=True) or {}
    message = payload.get("message", "").strip()

    if not message:
        return jsonify({"error": "Empty message"}), 400

    data = get_session_data()
    response, adaptation_note = build_response(message, data)

    return jsonify({
        "response": response,
        "adaptation": adaptation_note,
        "stats": {
            "stress_count": data["stress_count"],
            "edu_count": data["edu_count"],
            "positive_count": data["positive_count"]
        }
    })


@app.route("/reset", methods=["POST"])
def reset():
    """Clear the current session's stored data (privacy / fresh start)."""
    sid = session.get("sid")
    if sid and sid in SESSION_STORE:
        del SESSION_STORE[sid]
    session.clear()
    return jsonify({"status": "reset"})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
