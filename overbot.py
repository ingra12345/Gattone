import os
import requests
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# Server obbligatorio
threading.Thread(target=lambda: HTTPServer(('0.0.0.0', 10000), lambda *args: BaseHTTPRequestHandler(*args)).serve_forever(), daemon=True).start()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def test_immediato():
    print("--- TENTATIVO INVIO MESSAGGIO ---")
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        r = requests.post(url, json={"chat_id": CHAT_ID, "text": "🚩 ATTENZIONE: Se leggi questo, il bot è finalmente connesso!"})
        print(f"Risposta Telegram: {r.status_code}")
    except Exception as e:
        print(f"Errore invio: {e}")

test_immediato()

while True:
    print("Bot in attesa...")
    time.sleep(60)
    
