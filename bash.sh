cat > backend/gemini_service.py <<'EOF'
# -*- coding: utf-8 -*-
import os
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app) # Allows your React frontend to talk to this API

# 1. Configure Gemini
# Ensure your .env file has: GEMINI_API_KEY=your_actual_key_here
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

@app.route('/api/gemini-advice', methods=['POST'])
def get_advice():
    try:
        data = request.json
        material = data.get('material', 'unknown')
        location = data.get('city', 'India')

        # 2. Futuristic Prompt Engineering
        prompt = f"""
        Role: Futuristic Sustainability AI Architect.
        Context: Construction & Demolition (C&D) waste management in {location}.
        Target Material: {material}.
        
        Task: Provide a high-tech, actionable recycling protocol (max 45 words).
        Focus on: Industrial reuse, carbon offset potential, or recovery tech.
        Tone: Cyberpunk, clinical, and innovative. 
        Start with 'ANALYSIS:'
        """

        response = model.generate_content(prompt)
        
        return jsonify({
            "advice": response.text.strip(),
            "status": "NEURAL_LINK_ACTIVE"
        })

    except Exception as e:
        return jsonify({"advice": f"System Error: {str(e)}", "status": "LINK_OFFLINE"}), 500

if __name__ == "__main__":
    app.run(port=5001, debug=True)
EOF