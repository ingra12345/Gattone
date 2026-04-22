import os
import requests
import time
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# --- SERVER PER RENDER ---
class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self): 
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Gattone Online")
    def do_HEAD(self): 
        self.send_response(200)
        self.end_headers()

threading.Thread(target=lambda: HTTPServer(('0.0.0.0', 10000), HealthCheck).serve_forever(), daemon=True).start()

# --- CONFIGURAZIONE ---
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_KEY = os.getenv("API_KEY")

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")
    sys.stdout.flush()

def analizza_partite():
    url = "https://free-api-live-football-data.p.rapidapi.com/football-current-live"
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "free-api-live-football-data.p.rapidapi.com"
    }
    
    try:
        log("🔍 Controllo API...")
        res = requests.get(url, headers=headers, timeout=15)
        data = res.json()
        
        # Vediamo se la risposta contiene effettivamente delle partite
        partite = data.get("response", [])
        if not isinstance(partite, list):
            log(f"Risposta API insolita: {data}")
            return

        if len(partite) == 0:
            log("Nessuna partita live in questo momento.")
            return

        messaggio = f"⚽ **GATTONE LIVE UPDATE** ⚽\nPartite in corso: {len(partite)}\n"
        
        # Protezione: se partite non è una lista, questo non romperà il bot
        for p in partite[:10]:
            try:
                home = p.get('homeTeam', {}).get('name', 'Casa')
                away = p.get('awayTeam', {}).get('name', 'Fuori')
                score = p.get('status', {}).get('scoreStr', '0-0')
                messaggio += f"\n• {home} **{score}** {away}"
            except:
                continue

        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                      json={"chat_id": CHAT_ID, "text": messaggio, "parse_mode": "Markdown"})
        log("✅ Messaggio inviato!")

    except Exception as e:
        log(f"⚠️ Errore API: {e}")

# --- CICLO 15 MINUTI ---
log("--- BOT PRONTO (15 MIN) ---")
while True:
    analizza_partite()
    time.sleep(900)
    
