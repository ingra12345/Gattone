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

# Trucco per Render (Porta 10000)
class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Gattone Online")

def run_server():
    server = HTTPServer(('0.0.0.0', 10000), HealthCheck)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

def analizza():
    # URL specifico dell'API che hai trovato (Free API Live Football)
    url = "https://free-api-live-football-data.p.rapidapi.com/football-current-live"
    
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "free-api-live-football-data.p.rapidapi.com"
    }
    
    try:
        res = requests.get(url, headers=headers, timeout=10)
        data = res.json()
        
        # Questa API mette le partite dentro 'status' o 'response'
        # Proviamo a leggere la risposta
        partite = data.get("response", [])
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Scansione: trovati {len(partite)} match.")
        
        if len(partite) > 0:
            msg = f"✅ Gattone Online!\nSta monitorando {len(partite)} partite live."
            requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", 
                          json={"chat_id": TGID, "text": msg})
    except Exception as e:
        print(f"💥 Errore: {e}")

# Avvio
print("🚀 Gattone Bot avviato su Smart API...")
while True:
    analizza()
    time.sleep(600)
    
