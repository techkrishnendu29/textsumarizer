import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from summarizer import Summarizer, SummaryStyle

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)


@app.route('/api/summarize', methods=['POST', 'OPTIONS'])
def summarize_text():
    """
    POST endpoint to summarize text.
    
    Expected JSON:
    {
      "text": "Your long text here...",
      "style": "brief"  # optional: brief, bullet, detailed, keywords
    }
    """
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({"error": "Missing 'text' field"}), 400
        
        text = data.get('text', '').strip()
        style_name = data.get('style', 'brief').lower()
        
        # Validate text
        if len(text) < 10:
            return jsonify({"error": "Text must be at least 10 characters long"}), 400
        
        # Validate style
        valid_styles = [s.value for s in SummaryStyle]
        if style_name not in valid_styles:
            return jsonify({
                "error": f"Invalid style. Valid options: {', '.join(valid_styles)}"
            }), 400
        
        # Summarize
        summarizer = Summarizer()
        style = SummaryStyle(style_name)
        result = summarizer.summarize(text, style)
        
        # Return response
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
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route('/api/health', methods=['GET', 'OPTIONS'])
def health_check():
    """Health check endpoint."""
    if request.method == 'OPTIONS':
        return '', 204
    
    return jsonify({
        "status": "ok", 
        "service": "summarizer",
        "version": "1.0.0"
    }), 200


@app.route('/', methods=['GET'])
def index():
    """Root endpoint with API documentation."""
    return jsonify({
        "name": "Text Summarizer API",
        "version": "1.0.0",
        "endpoints": {
            "POST /api/summarize": "Summarize text",
            "GET /api/health": "Health check",
            "GET /": "API documentation"
        },
        "example": {
            "endpoint": "POST /api/summarize",
            "body": {
                "text": "Your long text here...",
                "style": "brief"
            },
            "styles": ["brief", "bullet", "detailed", "keywords"]
        }
    }), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
