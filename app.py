import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()  # בשימוש מקומי. ב-Vercel יש להגדיר Environment Variables בדשבורד

INSTANCE_ID = os.getenv("INSTANCE_ID")
GREEN_API_TOKEN = os.getenv("GREEN_API_TOKEN")

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello from Flask on Vercel! (Systeme-new-lead)"

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    """
    מצפה למבנה JSON דומה לזה:
    {
      "type": "contact.optin.completed",
      "data": {
        "funnel_step": {...},
        "contact": {
          "email": "...",
          "fields": {
            "phone_number": "...",
            "first_name": "...",
            "surname": "..."
          }
        },
        ...
      },
      "created_at": "2025-01-12T09:09:53+00:00"
    }
    """

    data = request.json  # מניחים ש-Content-Type הוא application/json

    # -- בדיקה בסיסית:
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid data format"}), 400

    # שליפת תאריך יצירת הליד
    created_at_str = data.get("created_at", "")
    created_at_formatted = format_iso_datetime(created_at_str)

    # שליפת פרטי ה-Funnel
    funnel_info = data.get("data", {}).get("funnel_step", {})
    # לפעמים תרצה דווקא funnel_info.get("funnel", {}).get("name")
    # אבל פה רואים שהשם הוא ב-funnel_step.name ( "Sales Page" )
    funnel_name = funnel_info.get("name", "לא ידוע")

    # שליפת פרטי איש הקשר
    contact_info = data.get("data", {}).get("contact", {})
    email = contact_info.get("email", "לא ידוע")

    # בתוך contact יש fields: { phone_number, first_name, surname }
    fields = contact_info.get("fields", {})
    phone = fields.get("phone_number", "לא ידוע")
    first_name = fields.get("first_name", "לא ידוע")
    last_name = fields.get("surname", "לא ידוע")

    # בניית הודעה
    message_text = (
        f"התקבל ליד חדש!\n"
        f"שם: {first_name} {last_name}\n"
        f"טלפון: {phone}\n"
        f"אימייל: {email}\n"
        f"Funnel: {funnel_name}\n"
        f"תאריך: {created_at_formatted}"
    )

    # שליחת ההודעה למספר שלך (66944164300)
    green_api_response = send_whatsapp_message("66944164300", message_text)

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
        "chatId": f"{phone}@c.us",
        "message": message
    }
    try:
        resp = requests.post(url, json=payload)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        return {"error": str(e)}

def format_iso_datetime(iso_str):
    """
    ממיר תאריך בפורמט ISO8601 ("2025-01-12T09:09:53+00:00")
    ל-DD/MM/YYYY HH:MM.
    אם לא מצליח, מחזיר את המחרוזת המקורית.
    """
    if not iso_str:
        return "לא ידוע"
    try:
        iso_str = iso_str.replace("Z", "")
        dt_obj = datetime.fromisoformat(iso_str)
        return dt_obj.strftime("%d/%m/%Y %H:%M")
    except ValueError:
        return iso_str
