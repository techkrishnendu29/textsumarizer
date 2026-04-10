import os
from flask import Flask, request, jsonify

from summarizer import Summarizer, SummaryStyle

app = Flask(__name__)

# ✅ FORCE CORS HEADERS ON EVERY RESPONSE
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response


# ✅ HANDLE PREFLIGHT (CRITICAL)
@app.route('/api/summarize', methods=['OPTIONS'])
def options_summarize():
    return '', 200


# ✅ MAIN API
@app.route('/api/summarize', methods=['POST'])
def summarize_text():
    try:
        data = request.get_json()

        if not data or 'text' not in data:
            return jsonify({"error": "Missing 'text' field"}), 400

        text = data.get('text', '').strip()
        style_name = data.get('style', 'brief').lower()

        if len(text) < 10:
            return jsonify({"error": "Text must be at least 10 characters long"}), 400

        valid_styles = [s.value for s in SummaryStyle]
        if style_name not in valid_styles:
            return jsonify({
                "error": f"Invalid style. Valid options: {', '.join(valid_styles)}"
            }), 400

        summarizer = Summarizer()
        style = SummaryStyle(style_name)
        result = summarizer.summarize(text, style)

        return jsonify({
            "success": True,
            "summary": result.summary
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ✅ HEALTH
@app.route('/api/health', methods=['GET', 'OPTIONS'])
def health():
    return jsonify({"status": "ok"})


# ✅ ROOT
@app.route('/')
def home():
    return "API running"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
