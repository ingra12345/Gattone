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
    except: pass

def analizza_partite():
    # URL AGGIORNATO: Questo è quello standard per i risultati del giorno
    url = "https://free-api-live-football-data.p.rapidapi.com/football-get-all-matches-by-date"
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "free-api-live-football-data.p.rapidapi.com"
    }
    
    try:
        oggi = time.strftime("%Y%m%d")
        log(f"🔍 Cerco match per la data: {oggi}")
        res = requests.get(url, headers=headers, params={"date": oggi}, timeout=15)
        data = res.json()
        
        # Struttura dati per questo specifico endpoint
        partite = data.get("response", {}).get("matches", [])
        
        if not partite:
            log(f"⚠️ Risposta API senza match. Dettaglio: {str(data)[:100]}")
            return

        msg = f"⚽ **GATTONE REPORT** ⚽\nMatch di oggi:\n"
        for p in partite[:10]:
            home = p.get('homeTeam', {}).get('name', 'N/A')
            away = p.get('awayTeam', {}).get('name', 'N/A')
            score = p.get('status', {}).get('scoreStr', 'vs')
            msg += f"\n• {home} {score} {away}"

        invia_telegram(msg)
        log(f"✅ Inviato messaggio con {len(partite[:10])} partite!")

    except Exception as e:
        log(f"⚠️ Errore: {e}")

# --- AVVIO ---
log("🚀 Bot in fase di test...")
invia_telegram("🔄 **TEST AVVIATO**\nControllo database in corso...")

while True:
    analizza_partite()
    time.sleep(900)
    
