import requests
import time
from flask import Flask, request
import os

app = Flask(__name__)

BOT_TOKEN = "1780245942:kRBIlWiNhtrfw2KMaVTbnoUqb7TDK4olePU"
GEMINI_TOKEN = "AQ.Ab8RN6KN5ah1SBfk7-tkjkZ0fZu2YzVrFPbdDS0z4LW-ZuYzlw"

histories = {}
user_last_request = {}

def ask_gemini(prompt, history):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={GEMINI_TOKEN}"
    context = "\n".join(history[-10:]) if history else ""
    full_prompt = f"{context}\nПользователь: {prompt}" if context else prompt
    payload = {"contents": [{"parts": [{"text": full_prompt}]}]}
    try:
        response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'}, timeout=30)
        data = response.json()
        return data['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"Ошибка Gemini: {str(e)}"

def send_message(chat_id, text):
    url = f"https://api.un1quedev.lol/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": text})
    except Exception as e:
        print(f"Ошибка отправки: {e}")

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    print(f"Получен запрос: {data}")
    if 'message' in data:
        chat_id = data['message']['chat']['id']
        text = data['message'].get('text', '')
        print(f"Сообщение от {chat_id}: {text}")
        if chat_id not in histories:
            histories[chat_id] = []
        if text == '/start':
            send_message(chat_id, "Привет! Я ИИ-помощник. Пиши вопросы.")
        elif text == 'Сбросить историю':
            histories[chat_id] = []
            send_message(chat_id, "История очищена!")
        else:
            t = time.time()
            if chat_id in user_last_request and t - user_last_request[chat_id] < 5:
                send_message(chat_id, f"⏳ Подожди {int(5 - (t - user_last_request[chat_id])) + 1} сек.")
                return "OK", 200
            user_last_request[chat_id] = t
            send_message(chat_id, "🤔 Генерирую ответ...")
            histories[chat_id].append(f"Ты: {text}")
            answer = ask_gemini(text, histories[chat_id])
            histories[chat_id].append(f"Бот: {answer}")
            send_message(chat_id, answer)
    return "OK", 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
