import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from PIL import Image

app = Flask(__name__)
CORS(app)

api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

SYSTEM_PROMPT = (
    "You are DRISHTI AI, an advanced AI accessibility companion designed specifically "
    "to empower blind and low-vision students in learning science, biology, geometry, and academic diagrams. "
    "When explaining images or diagrams, provide: "
    "1. Overview, "
    "2. Precise spatial layout and placement of every component, "
    "3. Functions and details of each part."
)

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DRISHTI AI - Diagram Scanner</title>
        <style>
            body { font-family: Arial, sans-serif; background: #fdfbf7; color: #333; padding: 20px; max-width: 800px; margin: auto; }
            h1 { color: #8b5a2b; }
            .box { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-top: 20px; }
            input, button { width: 100%; padding: 10px; margin-top: 10px; border-radius: 4px; box-sizing: border-box; }
            input { border: 1px solid #ccc; }
            button { background: #8b5a2b; color: white; border: none; font-size: 16px; cursor: pointer; }
            button:hover { background: #6b4423; }
            pre { background: #f4f4f4; padding: 15px; border-radius: 5px; white-space: pre-wrap; }
        </style>
    </head>
    <body>
        <h1>👁️ DRISHTI AI - Scanner</h1>
        <p>Upload any science diagram or photo for instant AI analysis.</p>
        
        <div class="box">
            <h3>Scan Diagram / Image</h3>
            <input type="file" id="imageInput" accept="image/*">
            <button onclick="scanImage()">Analyze Image with AI</button>
            <h4>Explanation:</h4>
            <pre id="result">Waiting for image...</pre>
        </div>

        <script>
            async function scanImage() {
                const fileInput = document.getElementById('imageInput');
                if(fileInput.files.length === 0) {
                    alert("Please select an image first!");
                    return;
                }
                document.getElementById('result').innerText = "Analyzing image with Gemini AI...";
                
                const formData = new FormData();
                formData.append('image', fileInput.files[0]);

                try {
                    const res = await fetch('/api/scan', {
                        method: 'POST',
                        body: formData
                    });
                    const data = await res.json();
                    if(data.success) {
                        document.getElementById('result').innerText = data.explanation;
                    } else {
                        document.getElementById('result').innerText = "Error: " + data.error;
                    }
                } catch(err) {
                    document.getElementById('result').innerText = "Request failed: " + err;
                }
            }
        </script>
    </body>
    </html>
    """

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "running", "message": "Backend active!"})

@app.route('/api/scan', methods=['POST'])
def scan_image():
    try:
        if 'image' not in request.files:
            return jsonify({"success": False, "error": "No image provided."}), 400
        
        image_file = request.files['image']
        image_path = "temp.png"
        image_file.save(image_path)
        img = Image.open(image_path)
        
        prompt = f"System Role: {SYSTEM_PROMPT}\nAnalyze this diagram for a student. Provide: 1. Summary, 2. Precise spatial placement of every part, 3. Functions of each part."
        
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
    
