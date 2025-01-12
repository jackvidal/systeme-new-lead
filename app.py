import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()  # לשימוש מקומי (ב-Vercel נשתמש ב-Environment Variables בלוח הבקרה)

INSTANCE_ID = os.getenv("INSTANCE_ID")
GREEN_API_TOKEN = os.getenv("GREEN_API_TOKEN")

app = Flask(__name__)

@app.route('/')
def index():
    """
    ראוט לשורש האתר כדי לוודא שהאפליקציה עובדת.
    """
    return "Hello from Flask on Vercel! (Systeme-new-lead)"

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    """
    ראוט המקבל את ה-JSON במבנה שאתה הצגת (מערך עם אובייקט אחד).
    לדוגמה:
    [
      {
        "type": "contact.optin.completed",
        "data": {
          "funnel_step": {...},
          "contact": {...},
          ...
        },
        "account": {...},
        "created_at": "2025-01-09T12:32:50+00:00"
      }
    ]
    """
    data = request.json  # מניח שה-Content-Type הוא application/json
    
    # מוודאים שקיבלנו מערך ובו לפחות אובייקט אחד
    if not isinstance(data, list) or len(data) == 0:
        return jsonify({"error": "Invalid data format"}), 400

    event_obj = data[0]

    # שליפת פרטי ה-Funnel
    funnel_info = event_obj.get('data', {}).get('funnel_step', {})
    funnel_name = funnel_info.get('funnel', {}).get('name', 'לא ידוע')

    # שליפת פרטי ה-Contact
    contact_info = event_obj.get('data', {}).get('contact', {})
    email = contact_info.get('email', 'לא ידוע')
    fields = contact_info.get('fields', {})
    phone = fields.get('phone_number', 'לא ידוע')
    first_name = fields.get('first_name', 'לא ידוע')
    last_name = fields.get('surname', 'לא ידוע')

    # תאריך יצירת הליד (מהשדה created_at). אפשר לפרמט אם תרצה
    created_at_str = event_obj.get('created_at', '')
    # לדוגמה, להמיר לפורמט DD/MM/YYYY
    # אם אתה רוצה רק תאריך בלי שעה:
    try:
        dt_obj = datetime.fromisoformat(created_at_str.replace("Z", ""))
        created_at_formatted = dt_obj.strftime("%d/%m/%Y %H:%M")
    except ValueError:
        created_at_formatted = created_at_str  # אם הפורמט לא תקין, נשתמש כמו שהוא

    # בניית הודעת הטקסט
    message_text = (
        f"התקבל ליד חדש מהאתר!\n"
        f"שם: {first_name} {last_name}\n"
        f"טלפון: {phone}\n"
        f"אימייל: {email}\n"
        f"Funnel: {funnel_name}\n"
        f"תאריך: {created_at_formatted}"
    )

    # שליחת ההודעה למספר שלך. 
    # החלף אם תרצה לשלוח לאותו "phone" של הליד, במקרה שהפורמט נכון.
    green_api_response = send_whatsapp_message("66944164300", message_text)

    return jsonify({
        "status": "success",
        "green_api_response": green_api_response
    })

def send_whatsapp_message(phone, message):
    """
    שליחת הודעת WhatsApp באמצעות Green API
    """
    url = f"https://api.green-api.com/waInstance{INSTANCE_ID}/SendMessage/{GREEN_API_TOKEN}"
    payload = {
        "chatId": f"{phone}@c.us",  # פורמט ללא "+"
        "message": message
    }
    try:
        resp = requests.post(url, json=payload)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        return {"error": str(e)}
