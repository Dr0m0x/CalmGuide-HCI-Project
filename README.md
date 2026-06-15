# CalmGuide - Adaptive Wellness Chatbot

CalmGuide is a Flask-based wellness chatbot that demonstrates AI-based
adaptive human-computer interaction through rule-based keyword detection
and session memory.

## Setup

```bash
pip install -r requirements.txt
python app.py
```

Then open http://localhost:5000 in your browser.

## How Adaptation Works

- The bot tracks counts of stress-related, educational, and positive
  messages for each session (stored temporarily in memory, never saved
  to disk).
- If a user mentions stress/anxiety keywords twice or more, the bot
  switches into "stress priority mode" and proactively offers breathing
  or grounding exercises with every response.
- If a user asks educational questions (e.g., "what is anxiety") twice
  or more, the bot switches to a more detailed informational response
  style.
- Positive feedback (e.g., "thanks", "feeling better") triggers
  encouraging follow-up messages.
- Click "Reset" to clear session data and start fresh.

## Files

- `app.py` - Flask server and adaptive logic
- `templates/index.html` - Chat interface
- `static/style.css` - Styling
- `static/script.js` - Frontend chat logic
- `requirements.txt` - Python dependencies

## AI Tool Usage Notes

- GitHub Copilot-style suggestions were used to scaffold the Flask
  route structure and the Fetch API call in script.js.
- ChatGPT-style assistance was used to organize the keyword dictionaries
  and brainstorm response variations.
- All AI-suggested code was reviewed, tested, and modified before
  inclusion.
