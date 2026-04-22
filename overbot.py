import os
import requests
import time
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# --- SERVER DI EMERGENZA PER RENDER ---
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
        r = requests.post(url, json={"chat_id": CHAT_ID, "text": testo, "parse_mode": "Markdown"}, timeout=10)
        log(f"Telegram status: {r.status_code}")
    except Exception as e:
        log(f"Errore Telegram: {e}")

def analizza_partite():
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "free-api-live-football-data.p.rapidapi.com"
    }
    
    try:
        log("🔍 Tentativo recupero dati...")
        # Proviamo a prendere i campionati principali (più probabile che abbiano dati)
        url = "https://free-api-live-football-data.p.rapidapi.com/football-all-matches-by-date"
        # Usiamo la data di oggi in formato YYYYMMDD
        oggi = time.strftime("%Y%m%d")
        res = requests.get(url, headers=headers, params={"date": oggi}, timeout=15)
        
        data = res.json()
        # Debug: stampiamo nei log la struttura per capire cosa arriva
        log(f"Risposta API: {str(data)[:100]}...") 

        partite = data.get("response", {}).get("matches", [])
        
        if not partite:
            # Se la lista è vuota, forse l'API vuole un'altra data o la chiave è errata
            log("❌ L'API ha risposto con 0 partite. Verifica API_KEY su Render.")
            return

        msg = f"⚽ **AGGIORNAMENTO PARTITE** ⚽\n\n"
        # Filtriamo solo le partite più importanti (prime 10)
        per_messaggio = partite[:10]
        for p in per_messaggio:
            home = p.get('homeTeam', {}).get('name', 'N/A')
            away = p.get('awayTeam', {}).get('name', 'N/A')
            status = p.get('status', {}).get('type', 'N/A')
            # Se è live mostra il punteggio, altrimenti l'ora
            score = p.get('status', {}).get('scoreStr', 'vs')
            msg += f"• {home} {score} {away} ({status})\n"

        invia_telegram(msg)
        log("✅ Messaggio inviato!")

    except Exception as e:
        log(f"⚠️ Errore durante il recupero: {e}")

# --- LOGICA DI AVVIO ---
log("🚀 Avvio sistema...")
invia_telegram("🤖 **GATTONE REBOOT**\nSe non ricevi partite tra 1 minuto, la tua API_KEY potrebbe essere scaduta o errata.")

while True:
    analizza_partite()
    time.sleep(900)
    
