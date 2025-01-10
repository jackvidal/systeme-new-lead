import os
from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv

# טוען את המשתנים מקובץ .env
load_dotenv()

# משיג את ה-InstanceID ואת ה-Token
INSTANCE_ID = os.getenv("INSTANCE_ID")
GREEN_API_TOKEN = os.getenv("GREEN_API_TOKEN")

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    """
    זהו הנתיב שאליו הטופס שלך שולח בקשת POST 
    לאחר שמישהו ממלא את הטופס (ומתרחש ה-Submit).
    """
    # במקרה שהבקשה מגיעה בפורמט JSON:
    data = request.json  
    # אם אתה מעדיף להגיע בפורמט form (x-www-form-urlencoded), אפשר להשתמש ב-request.form

    # דוגמה לשליפת נתונים רלוונטיים (phone, name, וכו'):
    phone_number = data.get('phone')
    lead_name = data.get('name', 'לקוח חדש')  # ברירת מחדל אם לא הגיע שם

    # הכנת ההודעה שרוצים לשלוח ב-WhatsApp
    message_text = f"התקבל ליד חדש מהאתר! שם: {lead_name}"

    # שליחת ההודעה
    result = send_whatsapp_message(phone_number, message_text)

    # החזרת תשובה (Response) לטופס/שירות שקרא לנו
    return jsonify({
        "status": "success",
        "green_api_response": result
    })


def send_whatsapp_message(phone, message):
    """
    פונקציה ששולחת הודעת WhatsApp באמצעות Green API
    """
    # כתובת ה-API של Green API עם הפרמטרים (Instance + Token)
    url = f"https://api.green-api.com/waInstance{INSTANCE_ID}/SendMessage/{GREEN_API_TOKEN}"

    payload = {
        "chatId": f"{phone}@c.us",  # במקרים מסוימים צריך להוסיף קידומת מדינה לפני המספר
        "message": message
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}

if __name__ == "__main__":
    # מפעילים את השרת המקומי בפורט 5000 (ניתן לשנות אם רוצים)
    app.run(debug=True, port=5000)
