import os
from flask import Flask, request, jsonify
import google.generativeai as genai
import pymongo

app = Flask(__name__)

# --- 1. CONFIGURATION ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")

# Ye Password hum Facebook ko denge (Aap ise badal sakte hain)
VERIFY_TOKEN = "sodha_agency_secret_123"

# --- 2. SETUP ---
genai.configure(api_key=GEMINI_API_KEY)
# Aapka fast model
model = genai.GenerativeModel('gemini-flash-latest') 

# MongoDB Setup
try:
    client = pymongo.MongoClient(MONGO_URI)
    db = client.get_database("ai_waiter_db")
    clients_collection = db.clients
    print("✅ Database Connected!")
except Exception as e:
    print(f"❌ Database Error: {e}")

# --- 3. ROUTES ---

@app.route('/', methods=['GET'])
def home():
    return "Raju AI Agency Server is Running! 🚀"

# (A) Browser Testing Route (Jo abhi hum use kar rahe the)
@app.route('/chat', methods=['GET'])
def chat():
    user_message = request.args.get('msg')
    client_id = request.args.get('client_id', '1001')
    
    if not user_message:
        return "Please send a message using ?msg=Hello"

    try:
        # Database se Client dhundo
        client_data = clients_collection.find_one({"client_id": client_id})
        if not client_data:
            return "Error: Client ID not found."

        bot_instruction = client_data['ai_config']['system_instruction']
        
        # Gemini se poocho
        response = model.generate_content(f"System: {bot_instruction}\nUser: {user_message}")
        return jsonify({"Raju_Says": response.text})
    except Exception as e:
        return jsonify({"error": str(e)})

# (B) WHATSAPP VERIFICATION ROUTE (Sabse Zaruri)
@app.route('/webhook', methods=['GET'])
def verify_webhook():
    # Facebook ye check karega
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    if mode and token:
        if mode == 'subscribe' and token == VERIFY_TOKEN:
            print("✅ Facebook Handshake Successful!")
            return challenge, 200
        else:
            print("❌ Wrong Token!")
            return 'Forbidden', 403
    return 'Bad Request', 400

# (C) WHATSAPP MESSAGE RECEIVER (Message aayega yahan)
@app.route('/webhook', methods=['POST'])
def receive_message():
    try:
        body = request.get_json()
        print("📩 New WhatsApp Message:", body)
        # Abhi hum sirf print kar rahe hain, reply baad mein jodenge
        return 'EVENT_RECEIVED', 200
    except Exception as e:
        print(f"Error: {e}")
        return 'ERROR', 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)

