import os
from flask import Flask, request, jsonify, render_template
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

@app.route('/')
def home():
    return render_template('index.html')

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
        
        # Real AI call using gemini-1.5-flash
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
    
