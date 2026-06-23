from flask import Flask, request, jsonify
from flask_cors import CORS
import anthropic
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ⚠️ PASTE YOUR NEW API KEY HERE
API_KEY = "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"

client = anthropic.Anthropic(api_key=API_KEY)

# Store logs in memory
logs_store = []

@app.route("/summarize", methods=["POST"])
def summarize():
    data = request.json
    log_text = data.get("log", "")
    therapist = data.get("therapist", "")
    mood = data.get("mood", "")

    if not log_text:
        return jsonify({"error": "No log provided"}), 400

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"""You are a medical assistant. Summarize this patient session log in 3-5 clear sentences for their therapist.

Therapist: {therapist}
Patient mood: {mood}
Patient log: {log_text}

Write only the summary, nothing else."""
        }]
    )

    summary = message.content[0].text

    logs_store.insert(0, {
        "date": datetime.now().strftime("%m/%d/%Y, %I:%M:%S %p"),
        "therapist": therapist,
        "mood": mood,
        "log": log_text,
        "summary": summary,
        "patient": "Jamie Santos"
    })

    return jsonify({"summary": summary})


@app.route("/logs", methods=["GET"])
def get_logs():
    return jsonify({"logs": logs_store})


@app.route("/simplify", methods=["POST"])
def simplify():
    data = request.json
    instructions = data.get("instructions", "")
    language = data.get("language", "English")

    if not instructions:
        return jsonify({"error": "No instructions provided"}), 400

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"""You are a helpful medical assistant. Translate these medical instructions into simple language a patient can understand. Write in {language}.

Medical instructions: {instructions}

Write only the simplified version, nothing else."""
        }]
    )

    simplified = message.content[0].text
    simplified = simplified.replace('**', '')
    return jsonify({"simplified": simplified})

# Store care plan
careplan_store = {"careplan": ""}

@app.route("/sendcareplan", methods=["POST"])
def send_careplan():
    data = request.json
    instructions = data.get("instructions", "")

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"""You are a helpful medical assistant. Translate these medical instructions into simple, clear language a patient can easily understand.

Medical instructions: {instructions}

Write only the simplified version, nothing else."""
        }]
    )

    simplified = message.content[0].text
# Remove markdown bold formatting
    simplified = simplified.replace('**', '')
    careplan_store["careplan"] = simplified


@app.route("/careplan", methods=["GET"])
def get_careplan():
    return jsonify(careplan_store)
if __name__ == "__main__":
    app.run(debug=True, port=5000)