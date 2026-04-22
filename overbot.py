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
        log("🔍 Controllo partite live...")
        res = requests.get(url, headers=headers, timeout=15)
        data = res.json()
        
        # CONTROLLO DI SICUREZZA: l'API deve restituire una lista
        partite = data.get("response", [])
        
        if not isinstance(partite, list) or len(partite) == 0:
            log("Nessuna partita live disponibile al momento.")
            return

        messaggio = f"⚽ **GATTONE LIVE UPDATE** ⚽\nPartite in corso: {len(partite)}\n"
        
        # Prende le prime 10 partite senza rischiare l'errore 'slice'
        for p in partite[:10]:
            try:
                home = p.get('homeTeam', {}).get('name', 'Casa')
                away = p.get('awayTeam', {}).get('name', 'Fuori')
                score = p.get('status', {}).get('scoreStr', '0-0')
                messaggio += f"\n• {home} **{score}** {away}"
            except:
                continue

        # Invio effettivo a Telegram
        r = requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                          json={"chat_id": CHAT_ID, "text": messaggio, "parse_mode": "Markdown"})
        
        if r.status_code == 200:
            log("✅ Messaggio inviato con successo!")
        else:
            log(f"❌ Errore Telegram: {r.text}")

    except Exception as e:
        log(f"⚠️ Errore imprevisto: {e}")

# --- CICLO 15 MINUTI ---
log("--- IL GATTONE È RIPARTITO ---")
while True:
    analizza_partite()
    time.sleep(900)
    
