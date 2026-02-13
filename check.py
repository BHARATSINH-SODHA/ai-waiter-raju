import os
import requests
from dotenv import load_dotenv

# 1. Tijori kholo
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# 2. Google se poocho "Kya available hai?"
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"

try:
    response = requests.get(url)
    data = response.json()
    
    print("\n--- AVAILABLE MODELS ---")
    if 'models' in data:
        for model in data['models']:
            # Sirf 'generateContent' wale models dikhao
            if "generateContent" in model['supportedGenerationMethods']:
                print(model['name'])
    else:
        print("Error:", data)
        
except Exception as e:
    print("Connection Error:", e)

