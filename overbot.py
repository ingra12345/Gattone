import os
import requests
import time
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# --- SERVER PER RENDER (Mantiene il servizio attivo) ---
class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self): 
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Gattone Online")
    def do_HEAD(self): 
        self.send_response(200)
        self.end_headers()

# Avvio server in background sulla porta 10000
def run_health_server():
    server = HTTPServer(('0.0.0.0', 10000), HealthCheck)
    server.serve_forever()

threading.Thread(target=run_health_server, daemon=True).start()

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
        log("🔍 Scansione partite live in corso...")
        res = requests.get(url, headers=headers, timeout=15)
        data = res.json()
        partite = data.get("response", [])
        
        if not partite:
            log("Nessuna partita live trovata in questo momento.")
            return

        messaggio = f"⚽ **GATTONE LIVE UPDATE** ⚽\n"
        messaggio += f"Partite in corso: {len(partite)}\n"
        messaggio += "---------------------------\n"
        
        # Mostriamo le prime 10 partite live
        for p in partite[:10]:
            home = p.get('homeTeam', {}).get('name', 'Casa')
            away = p.get('awayTeam', {}).get('name', 'Fuori')
            score = p.get('status', {}).get('scoreStr', '0-0')
            messaggio += f"\n• {home} **{score}** {away}"

        # Invio a Telegram
        r = requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                          json={"chat_id": CHAT_ID, "text": messaggio, "parse_mode": "Markdown"})
        
        if r.status_code == 200:
            log("✅ Messaggio inviato correttamente a Telegram.")
        else:
            log(f"❌ Errore Telegram: {r.text}")

    except Exception as e:
        log(f"⚠️ Errore API o Connessione: {e}")

# --- CICLO PRINCIPALE ---
log("--- IL GATTONE È OPERATIVO ---")
log("Frequenza impostata: 15 minuti.")

while True:
    analizza_partite()
    
    # 900 secondi = 15 minuti esatti
    time.sleep(900)
    
