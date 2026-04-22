import os
import requests
import time
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# --- SERVER PER RENDER ---
class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self): self.send_response(200); self.end_headers(); self.wfile.write(b"Gattone Online")
    def do_HEAD(self): self.send_response(200); self.end_headers()

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
        log("Controllo partite live...")
        res = requests.get(url, headers=headers, timeout=15)
        data = res.json()
        partite = data.get("response", [])
        
        if not partite:
            log("Nessuna partita live al momento.")
            return

        messaggio = f"⚽ **GATTONE LIVE UPDATE** ⚽\n\n"
        messaggio += f"Trovate {len(partite)} partite in corso:\n"
        
        # Prende le prime 10 partite per non fare un messaggio troppo lungo
        for p in partite[:10]:
            home = p.get('homeTeam', {}).get('name', 'Casa')
            away = p.get('awayTeam', {}).get('name', 'Fuori')
            score = p.get('status', {}).get('scoreStr', '0-0')
            messaggio += f"\n• {home} **{score}** {away}"

        # Invio a Telegram
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                      json={"chat_id": CHAT_ID, "text": messaggio, "parse_mode": "Markdown"})
        log("Messaggio inviato con successo!")

    except Exception as e:
        log(f"Errore durante l'analisi: {e}")

# --- CICLO PRINCIPALE ---
log("Il Gattone è operativo e analizzerà le partite ogni 15 minuti.")

while True:
    analizza_partite()
    # 900 secondi = 15 minuti. Puoi cambiare questo numero.
    time.sleep(900) 
