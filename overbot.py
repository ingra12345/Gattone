import os
import requests
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# 1. SERVER DI SERVIZIO PER RENDER (Corretto per evitare l'errore 501)
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Gattone Online")

def run_server():
    server = HTTPServer(('0.0.0.0', 10000), SimpleHandler)
    server.serve_forever()

# Avvia il server in un thread separato
threading.Thread(target=run_server, daemon=True).start()

# 2. CONFIGURAZIONE
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_KEY = os.getenv("API_KEY")

print("--- IL GATTONE SI STA SVEGLIANDO ---")

def test_telegram():
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": "🚩 CONNESSIONE RIUSCITA! Il bot è ora attivo e funzionante."}
    try:
        r = requests.post(url, json=payload)
        print(f"Test Telegram: {r.status_code}")
    except Exception as e:
        print(f"Errore Telegram: {e}")

# Invia un messaggio subito all'avvio
test_telegram()

# 3. CICLO DI CONTROLLO (Ogni 60 secondi)
while True:
    print(f"[{time.strftime('%H:%M:%S')}] Scansione in corso...")
    # Qui il bot lavora...
    time.sleep(60)
    
