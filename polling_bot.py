import requests
import time

BOT_TOKEN = "1780245942:kRBIlWiNhtrfw2KMaVTbnoUqb7TDK4olePU"
GEMINI_TOKEN = "AQ.Ab8RN6KN5ah1SBfk7-tkjkZ0fZu2YzVrFPbdDS0z4LW-ZuYzlw"

histories = {}
last_update_id = 0

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

def get_updates():
    global last_update_id
    url = f"https://api.un1quedev.lol/bot{BOT_TOKEN}/getUpdates?offset={last_update_id+1}&timeout=30"
    try:
        response = requests.get(url, timeout=35)
        return response.json()
    except Exception as e:
        print(f"Ошибка: {e}")
        return {}

print("🚀 Бот запущен!")

while True:
    try:
        updates = get_updates()
        if updates and 'result' in updates:
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
                            histories[chat_id].append(f"Ты: {text}")
                            answer = ask_gemini(text, histories[chat_id])
                            histories[chat_id].append(f"Бот: {answer}")
                            send_message(chat_id, answer)
        time.sleep(2)
    except Exception as e:
        print(f"Ошибка: {e}")
        time.sleep(5)
