import os
import requests
import time
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# Forza la stampa immediata nei log di Render
def log_print(msg):
    print(msg)
    sys.stdout.flush()

# Server per mantenere il servizio "Live"
class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self): self.send_response(200); self.end_headers(); self.wfile.write(b"OK")
    def do_HEAD(self): self.send_response(200); self.end_headers()

threading.Thread(target=lambda: HTTPServer(('0.0.0.0', 10000), HealthCheck).serve_forever(), daemon=True).start()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

log_print("--- AVVIO TEST AGGRESSIVO ---")
log_print(f"Target Chat: {CHAT_ID}")

while True:
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": "🔔 GATTONE: Test di invio forzato!"}
        r = requests.post(url, json=payload, timeout=10)
        
        log_print(f"Risposta Telegram: {r.status_code}")
        log_print(f"Dettaglio: {r.text}")
        
    except Exception as e:
        log_print(f"ERRORE CRITICO: {e}")
    
    time.sleep(30)
    
