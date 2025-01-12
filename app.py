import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

INSTANCE_ID = os.getenv("INSTANCE_ID")
GREEN_API_TOKEN = os.getenv("GREEN_API_TOKEN")

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello from Flask on Vercel! (Systeme-new-lead)"

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    """
    ראוט לקבלת POST מ-Systeme.io (או מכל מקור אחר).
    ננסה לכסות כמה תרחישים:
    1) גוף JSON פשוט (dict) {"phone":"...","name":"..."}
    2) גוף JSON שהוא מערך עם אובייקט (list) [ {...} ]
    3) Form Data
    """

    print(">>> Webhook called!")  # בדיקת גישה
    print("request.is_json:", request.is_json)
    print("request.json:", request.json)
    print("request.form:", request.form)

    # נשתמש במשתנה data כדי לאחסן את מה שנקרא
    data = None

    # 1) אם הבקשה מסומנת כ-JSON, ננסה לקרוא request.json
    if request.is_json:
        data = request.json
    else:
        # 2) יכול להיות שזה form data
        if request.form:
            # נהפוך את form ל-dict
            data = dict(request.form)
        else:
            data = None

    if data is None:
        # במקרה שלא הצלחנו לקרוא כלום
        print("No data found. Returning 400...")
        return jsonify({"error": "Invalid data format"}), 400

    # עכשיו נבדוק אם data הוא רשימה (list) או מילון (dict)
    if isinstance(data, list) and len(data) > 0:
        # נניח שזה המבנה של Systeme.io עם מערך ואובייקט אחד
        event_obj = data[0]

        # ננסה לחלץ את מה שהצגת בדוגמה:
        created_at_str = event_obj.get("created_at", "")
        dt_formatted = format_iso_datetime(created_at_str)

        funnel_info = event_obj.get("data", {}).get("funnel_step", {})
        funnel_name = funnel_info.get("name", "לא ידוע")

        contact_info = event_obj.get("data", {}).get("contact", {})
        email = contact_info.get("email", "לא ידוע")
        fields = contact_info.get("fields", {})
        phone = fields.get("phone_number", "לא ידוע")
        first_name = fields.get("first_name", "לא ידוע")
        last_name = fields.get("surname", "לא ידוע")

        message_text = (
            f"התקבל ליד חדש!\n"
            f"שם: {first_name} {last_name}\n"
            f"טלפון: {phone}\n"
            f"אימייל: {email}\n"
            f"Funnel: {funnel_name}\n"
            f"תאריך: {dt_formatted}"
        )

    elif isinstance(data, dict):
        # נניח שזה מבנה JSON פשוט {"phone":"...","name":"..."}
        # או שהפכנו form ל-dict
        
        # נבדוק אם יש phone, name פשוטים
        phone = data.get("phone", "לא ידוע")
        name = data.get("name", "לא ידוע")

        # לדוגמה, הוספת תאריך נוכחי במבנה dd/mm/yyyy
        dt_formatted = datetime.now().strftime("%d/%m/%Y")

        message_text = (
            f"התקבל ליד חדש!\n"
            f"שם: {name}\n"
            f"טלפון: {phone}\n"
            f"תאריך: {dt_formatted}"
        )
    else:
        # אם לא רשימה ולא dict
        print("Data is not dict or list. Returning 400...")
        return jsonify({"error": "Invalid data format"}), 400

    # כעת שולחים את ההודעה למספר שלך (66944164300). 
    # אם תרצה לשלוח למספר שהגיע מה-Webhook, תחליף ל-phone (ובתנאי שיש פורמט נכון).
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

def format_iso_datetime(iso_str):
    """
    ממיר מחרוזת בתבנית ISO8601 (למשל "2025-01-09T12:32:50+00:00")
    לפורמט נוח לקריאה (DD/MM/YYYY HH:MM).
    אם נכשל, מחזיר את המחרוזת המקורית.
    """
    if not iso_str:
        return "לא ידוע"
    try:
        iso_str = iso_str.replace("Z", "")  # למקרה שיש Z בסוף
        dt_obj = datetime.fromisoformat(iso_str)
        return dt_obj.strftime("%d/%m/%Y %H:%M")
    except ValueError:
        return iso_str
