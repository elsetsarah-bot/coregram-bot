import requests
import time
import threading
from flask import Flask
import os

app = Flask(__name__)

BOT_TOKEN = "1780245942:kRBIlWiNhtrfw2KMaVTbnoUqb7TDK4olePU"
GEMINI_TOKEN = "AQ.Ab8RN6KN5ah1SBfk7-tkjkZ0fZu2YzVrFPbdDS0z4LW-ZuYzlw"

histories = {}
last_update_id = 0

# Словарь для хранения времени последнего запроса каждого пользователя
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

def run_bot():
    global last_update_id
    print("🚀 Бот запущен! Ожидаю сообщения...")
    while True:
        try:
            url = f"https://api.un1quedev.lol/bot{BOT_TOKEN}/getUpdates?offset={last_update_id+1}&timeout=30"
            response = requests.get(url, timeout=35)
            updates = response.json()
            if 'result' in updates:
                for update in updates['result']:
                    update_id = update.get('update_id', 0)
                    if update_id > last_update_id:
                        last_update_id = update_id
                        if 'message' in update:
                            chat_id = update['message']['chat']['id']
                            text = update['message'].get('text', '')
                            if chat_id not in histories:
                                histories[chat_id] = []
                            print(f"Сообщение: {text}")
                            
                            if text == '/start':
                                send_message(chat_id, "Привет! Я ИИ-помощник. Пиши вопросы.")
                            elif text == 'Сбросить историю':
                                histories[chat_id] = []
                                send_message(chat_id, "История очищена!")
                            else:
                                # Проверяем ограничение
                                current_time = time.time()
                                last_time = user_last_request.get(chat_id, 0)
                                time_diff = current_time - last_time
                                
                                if time_diff < 5:
                                    wait_time = int(5 - time_diff) + 1
                                    send_message(chat_id, f"⏳ Подождите {wait_time} секунд перед следующим запросом.")
                                    continue
                                
                                user_last_request[chat_id] = current_time
                                
                                # Отправляем статус "Генерирую..."
                                send_message(chat_id, "🤔 Генерирую ответ...")
                                
                                histories[chat_id].append(f"Ты: {text}")
                                answer = ask_gemini(text, histories[chat_id])
                                histories[chat_id].append(f"Бот: {answer}")
                                
                                # Редактируем сообщение с ответом вместо "Генерирую..."
                                # Просто отправляем новое сообщение (API не поддерживает редактирование через polling)
                                send_message(chat_id, answer)
            time.sleep(2)
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(5)

@app.route('/')
def hello():
    return "Бот работает!"

if __name__ == '__main__':
    thread = threading.Thread(target=run_bot)
    thread.daemon = True
    thread.start()
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
