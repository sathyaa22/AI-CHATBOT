from flask import Flask, request, jsonify, render_template
import PyPDF2
import re

app = Flask(__name__)

# Load bad words from file
with open("bad_words.txt", "r") as f:
    bad_words = [w.strip().lower() for w in f.readlines()]

# Simple knowledge base
knowledge_base = {
    "hr": "Our HR policies include leave management, attendance tracking, and employee welfare programs.",
    "it": "The IT support team helps with password resets, network issues, and technical troubleshooting.",
    "event": "Upcoming events include the Annual Day celebration, Employee Recognition Week, and training workshops."
}

# Global variable to store uploaded document text
documents_text = ""

def check_bad_language(message):
    """Check if message contains any bad word."""
    message = message.lower()
    for word in bad_words:
        if word in message:
            return True
    return False


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "").lower()

    if not user_message:
        return jsonify({"reply": "Please enter a message."})

    # Check for bad words
    if check_bad_language(user_message):
        return jsonify({"reply": "Please avoid using inappropriate language."})

    # Match knowledge base keywords
    for key, value in knowledge_base.items():
        if key in user_message:
            return jsonify({"reply": value})

    # If document uploaded, try simple keyword matching
    global documents_text
    if documents_text:
        words = user_message.split()
        found = [w for w in words if w in documents_text.lower()]
        if found:
            snippet = " ".join(documents_text.split()[:40]) + "..."
            return jsonify({"reply": f"I found related information in your document: {snippet}"})

    # Default fallback
    return jsonify({"reply": "I'm not sure about that. Try asking about HR, IT, or company events."})


@app.route("/upload", methods=["POST"])
def upload():
    """Handle document upload and extract text."""
    global documents_text
    file = request.files.get("file")

    if not file:
        return jsonify({"reply": "No document uploaded."})

    try:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        documents_text = text
        return jsonify({"reply": "Document uploaded successfully and ready for use!"})
    except Exception as e:
        return jsonify({"reply": f"Error reading PDF: {e}"})


if __name__ == "__main__":
    app.run(debug=True)