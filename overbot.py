import os
import requests
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# --- CONFIGURAZIONE ---
API_KEY = os.getenv("API_KEY")
TG_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TGID = os.getenv("TELEGRAM_CHAT_ID")

# --- SERVER PER EVITARE ERRORI SU RENDER ---
class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Gattone Online")

def run_server():
    server = HTTPServer(('0.0.0.0', 10000), HealthCheck)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

# --- LOGICA BOT ---
def analizza():
    if not API_KEY or not TG_TOKEN:
        print("❌ Variabili mancanti su Render!")
        return

    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }
    
    try:
        res = requests.get(url, headers=headers, params={"live": "all"}, timeout=10)
        data = res.json()
        
        if data.get("errors"):
            print(f"⚠️ Errore API: {data['errors']}")
            return

        partite = data.get("response", [])
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Scansione: {len(partite)} match.")

        if len(partite) > 0:
            msg = f"🐈 Gattone Online! Vedo {len(partite)} partite."
            requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", 
                          json={"chat_id": TGID, "text": msg})
    except Exception as e:
        print(f"💥 Errore: {e}")

# --- AVVIO ---
print("🚀 Avvio in corso...")
while True:
    analizza()
    time.sleep(600)
    
