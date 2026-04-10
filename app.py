import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from summarizer import Summarizer, SummaryStyle

app = Flask(__name__)

# ✅ Correct CORS (handles OPTIONS automatically)
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=False)

@app.route('/api/summarize', methods=['POST'])
def summarize_text():
    data = request.get_json()

    if not data or 'text' not in data:
        return jsonify({"error": "Missing 'text' field"}), 400

    text = data.get('text', '').strip()
    style_name = data.get('style', 'brief').lower()

    if len(text) < 10:
        return jsonify({"error": "Text must be at least 10 characters long"}), 400

    valid_styles = [s.value for s in SummaryStyle]
    if style_name not in valid_styles:
        return jsonify({"error": f"Invalid style. Valid options: {', '.join(valid_styles)}"}), 400

    summarizer = Summarizer()
    style = SummaryStyle(style_name)
    result = summarizer.summarize(text, style)

    return jsonify({
        "success": True,
        "summary": result.summary
    }), 200


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200


@app.route('/')
def home():
    return "API running", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
