import os
from flask import Flask, request, jsonify
import google.generativeai as genai
import pymongo

app = Flask(__name__)

# --- 1. CONFIGURATION (Chabiyan) ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")

# --- 2. CONNECT TO SERVICES ---
# Gemini Setup
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-flash-latest')






# MongoDB Setup
try:
    client = pymongo.MongoClient(MONGO_URI)
    db = client.get_database("ai_waiter_db")
    clients_collection = db.clients
    print("✅ Database Connected!")
except Exception as e:
    print(f"❌ Database Error: {e}")

# --- 3. THE BRAIN (Dynamic Route) ---
@app.route('/chat', methods=['GET'])
def chat():
    user_message = request.args.get('msg')
    
    # Filhal hum default Client ID "1001" use karenge (Jo humne abhi banaya)
    # Baad mein ye WhatsApp number se automatic aayega
    client_id = request.args.get('client_id', '1001')

    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    try:
        # A. Database se Client ki Kundli nikalo
        client_data = clients_collection.find_one({"client_id": client_id})

        if not client_data:
            return jsonify({"AI_Response": "Error: Ye Client ID register mein nahi mili."})

        # B. Prompt nikalo (Example: "You are Raju Manager...")
        bot_instruction = client_data['ai_config']['system_instruction']
        bot_name = client_data['ai_config']['bot_name']

        # C. Gemini ko instruction do (System Prompt)
        # Hum naye chat session mein system instruction bhejte hain
        chat_session = model.start_chat(
            history=[
                {"role": "user", "parts": [f"System Instruction: {bot_instruction}"]},
                {"role": "model", "parts": ["Understood. I will act according to this instruction."]},
            ]
        )
        
        # D. Jawab mango
        response = chat_session.send_message(user_message)
        
        return jsonify({
            "Bot_Name": bot_name,
            "User": user_message,
            "AI_Response": response.text.strip()
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)

