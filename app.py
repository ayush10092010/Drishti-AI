import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from PIL import Image

app = Flask(__name__)
CORS(app)

# Configure API Key
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

SYSTEM_PROMPT = (
    "You are DRISHTI AI, an advanced AI accessibility companion designed specifically "
    "to empower blind and low-vision students in learning science, biology, geometry, and academic diagrams. "
    "When explaining images or diagrams, provide: "
    "1. Overview, "
    "2. Precise spatial layout and placement of every component, "
    "3. Functions and details of each part, "
    "4. Support for cross-questioning in English, Hindi, or Hinglish."
)

# Direct inline UI so 404 never happens even if templates folder is missing!
@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DRISHTI AI - Accessibility Companion</title>
        <style>
            body { font-family: Arial, sans-serif; background: #fdfbf7; color: #333; padding: 20px; max-width: 800px; margin: auto; }
            h1 { color: #8b5a2b; }
            .box { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-top: 20px; }
            textarea, input { width: 100%; padding: 10px; margin-top: 10px; border-radius: 4px; border: 1px solid #ccc; box-sizing: border-box; }
            button { background: #8b5a2b; color: white; border: none; padding: 10px 20px; margin-top: 10px; border-radius: 4px; cursor: pointer; font-size: 16px; }
            button:hover { background: #6b4423; }
            pre { background: #f4f4f4; padding: 15px; border-radius: 5px; white-space: pre-wrap; }
        </style>
    </head>
    <body>
        <h1>👁️ DRISHTI AI</h1>
        <p>Advanced AI Accessibility Companion for Blind & Low-Vision Students</p>
        
        <div class="box">
            <h3>Ask Science Question</h3>
            <textarea id="question" rows="3" placeholder="Ask any science or diagram question in English, Hindi, or Hinglish..."></textarea>
            <button onclick="askAI()">Ask AI</button>
            <h4>Response:</h4>
            <pre id="answer">Ready...</pre>
        </div>

        <script>
            async function askAI() {
                const q = document.getElementById('question').value;
                document.getElementById('answer').innerText = "Thinking...";
                try {
                    const res = await fetch('/api/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ question: q, language: 'English' })
                    });
                    const data = await res.json();
                    if(data.success) {
                        document.getElementById('answer').innerText = data.answer;
                    } else {
                        document.getElementById('answer').innerText = "Error: " + data.error;
                    }
                } catch(err) {
                    document.getElementById('answer').innerText = "Request failed: " + err;
                }
            }
        </script>
    </body>
    </html>
    """

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "running", "message": "Backend active!"})

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        question = data.get('question', '')
        language = data.get('language', 'English')
        
        prompt = f"User Language: {language}.\nSystem Role: {SYSTEM_PROMPT}\nQuestion: {question}\nAnswer clearly."
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        
        return jsonify({"success": True, "answer": response.text})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/scan', methods=['POST'])
def scan_image():
    try:
        if 'image' not in request.files:
            return jsonify({"success": False, "error": "No image provided."}), 400
        
        image_file = request.files['image']
        image_path = "temp.png"
        image_file.save(image_path)
        img = Image.open(image_path)
        
        prompt = f"System Role: {SYSTEM_PROMPT}\nAnalyze this diagram for a blind student. Provide: 1. Summary, 2. Precise spatial placement of every part, 3. Functions of each part."
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content([prompt, img])
        
        if os.path.exists(image_path):
            os.remove(image_path)
            
        return jsonify({"success": True, "explanation": response.text})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    
