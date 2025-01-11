import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()  # טוען משתני סביבה מקובץ .env (בשימוש מקומי, ב-Vercel יוגדר ב-Dashboard)

INSTANCE_ID = os.getenv("INSTANCE_ID")
GREEN_API_TOKEN = os.getenv("GREEN_API_TOKEN")

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello from Flask on Vercel! (Systeme-new-lead)"

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    """
    ראוט לקבלת נתונים מהטופס ב-Systeme.io
    """
    # בודקים אם הבקשה מגיעה כ-JSON או כ-form-urlencoded
    if request.is_json:
        data = request.json
    else:
        data = request.form

    # שליפת השדות (תעדכן את שמות השדות אם הם שונים ב-Systeme.io)
    first_name = data.get('first_name', 'לא ידוע')
    last_name = data.get('last_name', 'לא ידוע')
    email = data.get('email', 'לא ידוע')
    phone = data.get('phone', 'לא ידוע')

    # הוספת תאריך יצירת הליד בפורמט DD/MM/YYYY
    creation_date = datetime.now().strftime('%d/%m/%Y')

    # בניית הודעת הטקסט שתישלח בוואטסאפ
    message_text = (
        f"התקבל ליד חדש מהאתר!\n"
        f"שם: {first_name} {last_name}\n"
        f"טלפון: {phone}\n"
        f"אימייל: {email}\n"
        f"תאריך: {creation_date}"
    )

    # שליחת ההודעה למספר שלך (66944164300 - דוגמה) 
    # אם תרצה לשלוח לליד עצמו, אפשר להחליף ל-phone (בתנאי שהפורמט מתאים).
    green_api_response = send_whatsapp_message("66944164300", message_text)

    return jsonify({
        "status": "success",
        "green_api_response": green_api_response
    })

def send_whatsapp_message(phone, message):
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
