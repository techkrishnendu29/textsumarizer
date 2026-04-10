import os
from flask import Flask, request, jsonify
from summarizer import Summarizer, SummaryStyle

app = Flask(__name__)

# ✅ MANUAL CORS HANDLING (guaranteed)
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    return response


# ✅ Handle preflight globally
@app.route('/api/<path:path>', methods=['OPTIONS'])
def handle_options(path):
    return '', 200


# ✅ Summarize API
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
            "summary": result.summary,
            "style": result.style.value,
            "input_word_count": result.input_word_count,
            "output_word_count": result.output_word_count,
            "sentence_count_in": result.sentence_count_in,
            "sentence_count_out": result.sentence_count_out,
            "top_keywords": result.top_keywords,
            "elapsed_seconds": result.elapsed_seconds,
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ✅ Health
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"}), 200


# ✅ Root
@app.route('/')
def index():
    return jsonify({"message": "API running"}), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
