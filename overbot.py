import os
import requests
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# Risposta per Render
class S(BaseHTTPRequestHandler):
    def do_GET(self): self.send_response(200); self.end_headers(); self.wfile.write(b"OK")
    def do_HEAD(self): self.send_response(200); self.end_headers()

threading.Thread(target=lambda: HTTPServer(('0.0.0.0', 10000), S).serve_forever(), daemon=True).start()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def test_invio():
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": "🚀 GATTone: Sistema agganciato con successo!"}
    try:
        r = requests.post(url, json=payload, timeout=10)
        print(f"--- RISULTATO INVIO ---")
        print(f"Stato: {r.status_code}")
        print(f"Risposta: {r.text}")
    except Exception as e:
        print(f"Errore tecnico: {e}")

# Primo invio immediato
test_invio()

# Poi ogni 10 minuti
while True:
    time.sleep(600)
    test_invio()
    
