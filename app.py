import os
import requests
from flask import Flask, request, jsonify
import google.generativeai as genai
import pymongo

app = Flask(__name__)

# --- CONFIGURATION ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")

# ⚠️ YAHAN APNA FACEBOOK TOKEN PASTE KAREIN (Quotes "" ke andar)
FB_ACCESS_TOKEN = "EAANAZAP21dmIBQhSulFOBzLitCZAguF8JjqyZBwthzLBwe2pHeaXTjrnu4hJu4xkKCC27crvgXsh9opGRdNLmBdXkQE0fBv1Tfxj5hLSZAv43eVGH47IXrlNEQyW6vSmeyyO7RzQpQsCl1IBaRai6bgWmhKsHl9G2SVA6xbmJ8BNwZChgdiYBy9JodY2qpDbMJldKKmL7xw09hmdvjDfyeBGc1lpIv7JVCbYrT9yksPgZBcgfak56TxrIZBA1wNoZBd3HDK8DzQJDoPwGIDwCfbb"

# Verify Token (Jo Facebook App setting mein dala tha)
VERIFY_TOKEN = "sodha_agency_secret_123"

# --- SETUP ---
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-flash-latest')

# Database
try:
    client = pymongo.MongoClient(MONGO_URI)
    db = client.get_database("ai_waiter_db")
    clients_collection = db.clients
except Exception as e:
    print(f"Database Error: {e}")

# --- FUNCTION: SEND WHATSAPP MESSAGE ---
def send_whatsapp_message(to_number, message_text):
    url = "https://graph.facebook.com/v21.0/1043644368824801/messages"
    headers = {
        "Authorization": f"Bearer {FB_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": message_text}
    }
    response = requests.post(url, json=data, headers=headers)
    print(f"Message Sent: {response.status_code}")

# --- ROUTES ---
@app.route('/', methods=['GET'])
def home():
    return "Raju is Alive and Speaking! 🤖"

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if mode == 'subscribe' and token == VERIFY_TOKEN:
        return challenge, 200
    return 'Forbidden', 403

@app.route('/webhook', methods=['POST'])
def receive_message():
    try:
        body = request.get_json()
        
        # Check agar message user se aaya hai
        if body.get("object") == "whatsapp_business_account":
            for entry in body["entry"]:
                for change in entry["changes"]:
                    if change["value"].get("messages"):
                        msg_data = change["value"]["messages"][0]
                        user_phone = msg_data["from"]
                        user_msg = msg_data["text"]["body"]
                        
                        print(f"User {user_phone} says: {user_msg}")

                        # 1. Database se Raju (Client 1001) ki personality nikalo
                        # (Filhal hum har kisi ko Raju Manager hi denge)
                        client_data = clients_collection.find_one({"client_id": "1001"})
                        
                        if client_data:
                            system_instruction = client_data['ai_config']['system_instruction']
                            
                            # 2. Gemini AI se jawab mango
                            response = model.generate_content(f"System: {system_instruction}\nUser: {user_msg}")
                            ai_reply = response.text
                            
                            # 3. Wapas WhatsApp par bhejo
                            send_whatsapp_message(user_phone, ai_reply)
                        else:
                            print("Client 1001 not found in DB")

        return 'EVENT_RECEIVED', 200
    except Exception as e:
        print(f"Error: {e}")
        return 'EVENT_RECEIVED', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)

