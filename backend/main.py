import os
import io
import json
import uvicorn
import mysql.connector
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from PIL import Image
from ultralytics import YOLO
from google import genai

# --- 1. CONFIGURATION ---
load_dotenv() 

# A. Configure Gemini (Only for advice, not detection)
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
gemini_client = None
if GEMINI_API_KEY:
    try:
        gemini_client = genai.Client(api_key=GEMINI_API_KEY)
    except:
        pass

# B. Configure YOLO (Your Custom Model)
try:
    # Load YOUR trained model
    model = YOLO("best.pt") 
    print("✅ Custom YOLO Model (best.pt) Loaded Successfully!")
except Exception as e:
    print(f"❌ Error loading best.pt: {e}")
    print("   Make sure 'best.pt' is in the backend folder.")
    model = None

app = FastAPI(title="Smart Construction Waste Manager")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    try:
        return mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            database=os.getenv("DB_NAME"),
            port=int(os.getenv("DB_PORT"))
        )
    except Exception as e:
        print(f"❌ DB Connection Error: {e}")
        return None

# --- 2. HELPER: GET ADVICE ---
def get_recycling_advice(waste_type):
    """Uses Gemini to generate advice based on YOLO's detection"""
    if not gemini_client:
        return "Recycle according to local construction guidelines."
    
    try:
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"Give me 2 short sentences on how to recycle construction waste of type: {waste_type}."
        )
        return response.text.strip()
    except:
        return "Standard recovery protocol applies."

# --- 3. API ENDPOINTS ---

@app.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    if not model:
        raise HTTPException(status_code=500, detail="YOLO Model not loaded. Check server logs.")

    # 1. Read Image
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))

    # 2. Run YOLO Inference (The "Prediction" step)
    print("🤖 Running best.pt inference...")
    results = model(image)
    
    # 3. Process Results
    detected_class = "Unknown"
    confidence = 0.0
    
    # Get the object with highest confidence
    if len(results) > 0 and len(results[0].boxes) > 0:
        box = results[0].boxes[0]
        class_id = int(box.cls[0])
        detected_class = model.names[class_id] # e.g., "Concrete"
        confidence = float(box.conf[0])
    
    print(f"✅ YOLO Detected: {detected_class} ({confidence:.2f})")

    # 4. Get Advice (Optional, from Gemini)
    advice = get_recycling_advice(detected_class)

    # 5. Save to AWS Database
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            query = "INSERT INTO scans (waste_type, confidence, gemini_advice) VALUES (%s, %s, %s)"
            cursor.execute(query, (detected_class, confidence, advice))
            conn.commit()
            scan_id = cursor.lastrowid
            cursor.close()
            conn.close()
            return {
                "scan_id": scan_id,
                "waste_type": detected_class,
                "confidence": confidence,
                "advice": advice
            }
    except Exception as e:
        print(f"⚠️ DB Save Error: {e}")
    
    return {
        "waste_type": detected_class,
        "confidence": confidence,
        "advice": advice,
        "note": "Data not saved to DB due to connection error"
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

# --- PHASE 4 UPDATES ---

@app.get("/centers")
def get_recycling_centers():
    """Fetch all recycling centers from AWS RDS"""
    try:
        conn = get_db_connection()
        if not conn:
            return []
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT name, address, latitude, longitude, contact_info FROM recycling_centers")
        centers = cursor.fetchall()
        
        cursor.close()
        conn.close()
        return centers
    except Exception as e:
        print(f"Error fetching centers: {e}")
        return []

@app.get("/history")
def get_scan_history():
    """Fetch last 10 scans"""
    try:
        conn = get_db_connection()
        if not conn:
            return []
        
        cursor = conn.cursor(dictionary=True)
        # Order by newest first
        cursor.execute("SELECT id, waste_type, confidence, timestamp, gemini_advice FROM scans ORDER BY id DESC LIMIT 10")
        history = cursor.fetchall()
        
        cursor.close()
        conn.close()
        return history
    except Exception as e:
        print(f"Error fetching history: {e}")
        return []

# --- HEALTH CHECK ENDPOINT ---
@app.get("/health")
def check_data_connectivity():
    """
    Robust health check: Validates actual SQL execution.
    """
    try:
        # 1. Attempt to connect
        conn = get_db_connection()
        if not conn:
            raise HTTPException(status_code=503, detail="Database Connection Failed")
        
        # 2. Attempt to run a real query
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        
        # 3. Clean up
        cursor.close()
        conn.close()
        
        return {
            "status": "online", 
            "database": "AWS RDS (MySQL)", 
            "data_flow": "active", 
            "query_result": result[0]
        }
        
    except Exception as e:
        print(f"❌ Connectivity Error: {e}")
        raise HTTPException(status_code=500, detail=f"Data Connectivity Error: {str(e)}")
