import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()  # טוען משתני סביבה מקובץ .env בעת עבודה מקומית (לא יפעל אוטומטית ב-Vercel)

# שליפת משתני הסביבה
INSTANCE_ID = os.getenv("INSTANCE_ID")
GREEN_API_TOKEN = os.getenv("GREEN_API_TOKEN")

app = Flask(__name__)

@app.route('/')
def index():
    """
    ראוט לשורש האתר, רק כדי לבדוק שהאפליקציה פועלת.
    """
    return "Hello from Flask on Vercel! (Systeme-new-lead)"

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    """
    ראוט שאליו המערכת (או הטופס) שולחת את בקשת ה-POST עם פרטי הליד.
    """
    data = request.json  # הנחה שהפורמט הוא application/json
    lead_name = data.get('name', 'לקוח חדש')
    # במקרה הנוכחי, מתעלמים מהטלפון שמגיע מה-POST ושולחים *תמיד* אל המספר שלך
    phone_number = "66944164300"

    message_text = f"התקבל ליד חדש מהאתר: {lead_name}"

    # שליחת ההודעה דרך Green API
    green_api_response = send_whatsapp_message(phone_number, message_text)

    return jsonify({
        "status": "success",
        "green_api_response": green_api_response
    })

def send_whatsapp_message(phone, message):
    """
    שולח הודעת WhatsApp באמצעות Green API.
    """
    # כתובת ה-API בהתאם ל-InstanceID ול-Token שב-ENV
    url = f"https://api.green-api.com/waInstance{INSTANCE_ID}/SendMessage/{GREEN_API_TOKEN}"
    payload = {
        # פורמט '66944164300@c.us' -> ללא '+' וללא רווחים
        "chatId": f"{phone}@c.us",
        "message": message
    }
    try:
        resp = requests.post(url, json=payload)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        return {"error": str(e)}

# ב-Vercel אין צורך ב- app.run() כי זה Serverless, לכן משאירים רק את הקוד לעיל.
