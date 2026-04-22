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

def run_server():
    httpd = HTTPServer(('0.0.0.0', 10000), HealthCheck)
    httpd.serve_forever()

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
    payload = {"chat_id": CHAT_ID, "text": testo, "parse_mode": "Markdown"}
    try:
        r = requests.post(url, json=payload, timeout=10)
        return r.status_code == 200
    except:
        return False

def analizza_partite():
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "free-api-live-football-data.p.rapidapi.com"
    }
    
    try:
        log("🔍 Controllo partite...")
        # 1. Prova i LIVE
        res_live = requests.get("https://free-api-live-football-data.p.rapidapi.com/football-current-live", headers=headers, timeout=15)
        data_live = res_live.json()
        partite = data_live.get("response", [])

        if isinstance(partite, list) and len(partite) > 0:
            msg = "⚽ **GATTONE LIVE UPDATE** ⚽\n"
            for p in partite[:10]:
                home = p.get('homeTeam', {}).get('name', 'N/A')
                away = p.get('awayTeam', {}).get('name', 'N/A')
                score = p.get('status', {}).get('scoreStr', '0-0')
                msg += f"\n• {home} **{score}** {away}"
            invia_telegram(msg)
            log("✅ Inviato LIVE")
        else:
            # 2. Se no LIVE, prova PROGRAMMA OGGI
            log("Nessun live. Controllo programma oggi...")
            today = time.strftime("%Y%m%d")
            res_today = requests.get(f"https://free-api-live-football-data.p.rapidapi.com/football-all-matches-by-date?date={today}", headers=headers, timeout=15)
            data_today = res_today.json()
            matches = data_today.get("response", {}).get("matches", [])
            
            if matches:
                msg = f"📅 **PROGRAMMA DI OGGI ({time.strftime('%d/%m')})** 📅\n"
                for m in matches[:12]:
                    h = m.get('homeTeam', {}).get('name', 'N/A')
                    a = m.get('awayTeam', {}).get('name', 'N/A')
                    ora = m.get('status', {}).get('startTimeStr', '--:--')
                    msg += f"\n• {h} vs {a} (Ore {ora})"
                invia_telegram(msg)
                log("✅ Inviato programma")
            else:
                log("Niente da segnalare per ora.")
    except Exception as e:
        log(f"⚠️ Errore API: {e}")

# --- AVVIO ---
log("🚀 Avvio sistema...")
invia_telegram("🔔 **GATTONE ONLINE**\nControllo ogni 15 minuti attivato!")

while True:
    analizza_partite()
    time.sleep(900)
    
