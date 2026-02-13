import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def ask_gemini(message):
    if not GEMINI_API_KEY:
        return "Error: API Key nahi mili!"

    # CHANGE: Humne model ka naam 'gemini-1.5-flash' se badal kar 'gemini-pro' kar diya hai
    # Ye purana model hai par kabhi fail nahi hota.
       
    # UPDATE: Hum 'gemini-1.5-flash' use kar rahe hain jo free tier mein sabse stable hai
        # UPDATE: Ye naam aapke screenshot mein saaf dikh raha hai
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={GEMINI_API_KEY}"

    
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{
            "parts": [{
                "text": f"You are a helpful waiter named Raju. Keep answers short. Customer asks: {message}"
            }]
        }]
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code != 200:
            return f"Google Error: {response.text}"
            
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        
    except Exception as e:
        return f"Connection Error: {str(e)}"

@app.route("/")
def home():
    return "🚀 AI Waiter is Running (Stable Mode)!"

@app.route("/chat")
def chat():
    user_msg = request.args.get("msg", "Hello")
    reply = ask_gemini(user_msg)
    return jsonify({"User": user_msg, "AI_Raju": reply})

if __name__ == "__main__":
    app.run(debug=True, port=5000)

