import os
import requests
import time
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# --- SERVER PER RENDER ---
class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self): 
        self.send_response(200); self.end_headers(); self.wfile.write(b"Gattone Online")

threading.Thread(target=lambda: HTTPServer(('0.0.0.0', 10000), HealthCheck).serve_forever(), daemon=True).start()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_KEY = os.getenv("API_KEY")

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}"); sys.stdout.flush()

def invia_telegram(testo):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": testo, "parse_mode": "Markdown"}, timeout=10)
    except Exception as e:
        log(f"Errore Telegram: {e}")

def analizza_partite():
    # Endpoint corretto per tutte le partite
    url = "https://free-api-live-football-data.p.rapidapi.com/football-get-all-matches"
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "free-api-live-football-data.p.rapidapi.com"
    }
    
    try:
        log("🔍 Recupero partite con nuovo endpoint...")
        # L'API richiede il giorno attuale
        oggi = time.strftime("%Y%m%d")
        res = requests.get(url, headers=headers, params={"day": oggi}, timeout=15)
        data = res.json()
        
        # Estraiamo le partite dalla nuova struttura dell'API
        partite = data.get("response", {}).get("status", {}).get("allMatches", [])
        
        if not partite:
            log("⚠️ Nessuna partita trovata. Verifica se l'API_KEY è attiva su RapidAPI.")
            return

        msg = f"⚽ **GATTONE FOOTBALL REPORT** ⚽\n\n"
        # Prendiamo le prime 10 partite per non intasare Telegram
        count = 0
        for p in partite:
            if count >= 10: break
            home = p.get('homeTeam', {}).get('name', 'N/A')
            away = p.get('awayTeam', {}).get('name', 'N/A')
            # Recupero del punteggio o dell'orario
            status = p.get('status', {}).get('type', 'N/A')
            score = p.get('status', {}).get('scoreStr', 'vs')
            
            msg += f"• {home} {score} {away} ({status})\n"
            count += 1

        invia_telegram(msg)
        log(f"✅ Inviate {count} partite!")

    except Exception as e:
        log(f"⚠️ Errore API: {e}")

# --- AVVIO ---
log("🚀 Sistema riavviato con nuovi endpoint!")
invia_telegram("🤖 **GATTONE AGGIORNATO**\nEndpoint corretti. Controllo partite ogni 15 minuti.")

while True:
    analizza_partite()
    time.sleep(900)
    
