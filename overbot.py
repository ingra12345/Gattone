import os
import requests
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# 1. SERVER MINIMO (Evita l'errore 501)
class S(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Gattone OK")

def run():
    httpd = HTTPServer(('0.0.0.0', 10000), S)
    httpd.serve_forever()

threading.Thread(target=run, daemon=True).start()

# 2. CONFIGURAZIONE
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

print("--- IL GATTONE E' PARTITO ---")

# 3. CICLO DI INVIO
while True:
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        r = requests.post(url, json={"chat_id": CHAT_ID, "text": "🐈 GATTONE: Se leggi questo, la connessione è OK!"})
        print(f"[{time.strftime('%H:%M:%S')}] Tentativo invio... Stato: {r.status_code}")
    except Exception as e:
        print(f"Errore: {e}")
    time.sleep(30)
    
