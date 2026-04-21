import os
import requests
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# Server per tenere in vita il servizio su Render
threading.Thread(target=lambda: HTTPServer(('0.0.0.0', 10000), lambda *args: BaseHTTPRequestHandler(*args)).serve_forever(), daemon=True).start()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

print("--- DIAGNOSTICA AVVIATA ---")
print(f"Token presente: {'SI' if TOKEN else 'NO'}")
print(f"Chat ID presente: {'SI' if CHAT_ID else 'NO'}")

def invia_test():
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        r = requests.post(url, json={"chat_id": CHAT_ID, "text": "🐈 GATTone: Se leggi questo, funziona tutto!"}, timeout=10)
        if r.status_code == 200:
            print("✅ MESSAGGIO INVIATO CON SUCCESSO!")
        else:
            print(f"❌ ERRORE TELEGRAM: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"💥 ERRORE DI CONNESSIONE: {e}")

# Prova a inviare ogni 30 secondi
while True:
    invia_test()
    time.sleep(30)
