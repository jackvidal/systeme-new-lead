import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()  # אם תרצה לטעון את .env מקומית

INSTANCE_ID = os.getenv("INSTANCE_ID")
GREEN_API_TOKEN = os.getenv("GREEN_API_TOKEN")

app = Flask(__name__)

@app.route('/')
def index():
    """
    ראוט לשורש האתר, רק כדי שיהיה ברור שהאפליקציה עולה.
    """
    return "Hello from Flask on Vercel! (Systeme-new-lead)"

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    """
    ראוט לקבלת POST מהטופס
    """
    data = request.json  # אם הסוג הוא application/json
    phone_number = data.get('phone')
    lead_name = data.get('name', 'לקוח חדש')

    message_text = f"התקבל ליד חדש: {lead_name}"
    green_api_response = send_whatsapp_message(phone_number, message_text)

    return jsonify({
        "status": "success",
        "green_api_response": green_api_response
    })

def send_whatsapp_message(phone, message):
    """
    שולח הודעת WhatsApp בעזרת Green API
    """
    url = f"https://api.green-api.com/waInstance{INSTANCE_ID}/SendMessage/{GREEN_API_TOKEN}"
    payload = {
        "chatId": f"{phone}@c.us",  # בדוק את הפורמט לפי המדינה
        "message": message
    }
    try:
        resp = requests.post(url, json=payload)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        return {"error": str(e)}

# ב־Vercel אין צורך ב־app.run() כי זה Serverless,
# לכן משאירים את זה ככה.
