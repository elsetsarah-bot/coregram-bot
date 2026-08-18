import requests
from flask import Flask, request
import os

app = Flask(__name__)

BOT_TOKEN = "1780245942:kRBIlWiNhtrfw2KMaVTbnoUqb7TDK4olePU"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    print(f"Получен запрос: {data}")
    
    if 'message' in data:
        chat_id = data['message']['chat']['id']
        text = data['message'].get('text', '')
        print(f"Сообщение от {chat_id}: {text}")
        
        # Отправляем простой ответ
        url = f"https://api.un1quedev.lol/bot{BOT_TOKEN}/sendMessage"
        try:
            requests.post(url, json={"chat_id": chat_id, "text": "Привет, я живой!"})
            print("Ответ отправлен!")
        except Exception as e:
            print(f"Ошибка отправки: {e}")
    
    return "OK", 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
