import os
import requests
import time
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# --- SERVER DI CONTROLLO PER RENDER (Evita lo standby) ---
class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self): 
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Gattone Online")

def run_server():
    # Usa la porta 10000 come richiesto da Render
    server = HTTPServer(('0.0.0.0', 10000), HealthCheck)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

# --- CONFIGURAZIONE ---
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_KEY = os.getenv("API_KEY")

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")
    sys.stdout.flush()

def invia_telegram(testo):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID, 
        "text": testo, 
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        log(f"Errore Telegram: {e}")

def analizza_partite():
    # Endpoint corretto per la tua API specifica
    url = "https://free-api-live-football-data.p.rapidapi.com/football-get-all-matches"
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "free-api-live-football-data.p.rapidapi.com"
    }
    
    try:
        log("🔍 Controllo partite in corso...")
        # Aggiungiamo il parametro della data per sicurezza
        oggi = time.strftime("%Y%m%d")
        res = requests.get(url, headers=headers, params={"date": oggi}, timeout=15)
        
        if res.status_code != 200:
            log(f"⚠️ Errore API (Codice {res.status_code}): {res.text}")
            return

        data = res.json()
        # Estraiamo i match dalla risposta
        partite = data.get("response", {}).get("matches", [])
        
        if not partite:
            log(f"⚠️ Nessuna partita trovata nel database per oggi ({oggi}).")
            return

        messaggio = f"⚽ **GATTONE REPORT** ⚽\nPartite di oggi:\n"
        
        # Prendiamo le prime 10 partite per non fare messaggi troppo lunghi
        count = 0
        for p in partite[:10]:
            home = p.get('homeTeam', {}).get('name', 'N/A')
            away = p.get('awayTeam', {}).get('name', 'N/A')
            # Cerchiamo il punteggio o l'orario
            status = p.get('status', {}).get('type', 'N/A')
            score = p.get('status', {}).get('scoreStr', 'vs')
            
            messaggio += f"\n• {home} **{score}** {away} ({status})"
            count += 1

        invia_telegram(messaggio)
        log(f"✅ Inviato messaggio con {count} partite!")

    except Exception as e:
        log(f"⚠️ Errore critico: {e}")

# --- AVVIO BOT ---
log("🚀 Bot avviato! In attesa di dati...")
invia_telegram("🤖 **IL GATTONE È TORNATO**\nControllo database avviato!")

while True:
    analizza_partite()
    # Controlla ogni 15 minuti
    time.sleep(900)
    
