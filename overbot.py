import os
import requests
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# 1. SERVER CHE RISPONDE A RENDER (GESTISCE HEAD E GET)
class RenderHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Gattone is Live")
        
    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

def run_server():
    server = HTTPServer(('0.0.0.0', 10000), RenderHandler)
    server.serve_forever()

# Avvio server in background
threading.Thread(target=run_server, daemon=True).start()

# 2. CONFIGURAZIONE (CARICATA DA RENDER)
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

print("--- IL GATTONE SI STA SVEGLIANDO ---")

# 3. CICLO DI INVIO MESSAGGI
while True:
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": "✅ GATTONE SBLOCCATO! Se leggi questo, il bot sta finalmente lavorando."}
        r = requests.post(url, json=payload, timeout=10)
        
        # Stampiamo nei log cosa succede
        print(f"[{time.strftime('%H:%M:%S')}] Tentativo invio Telegram... Stato: {r.status_code}")
        
        if r.status_code != 200:
            print(f"⚠️ Dettaglio errore: {r.text}")
            
    except Exception as e:
        print(f"💥 Errore connessione: {e}")
        
    time.sleep(30)
    
