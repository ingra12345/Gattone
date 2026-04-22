import os, requests, time, sys, threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# Server per mantenere vivo il bot su Render
class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self): 
        self.send_response(200); self.end_headers(); self.wfile.write(b"OK")

threading.Thread(target=lambda: HTTPServer(('0.0.0.0', 10000), HealthCheck).serve_forever(), daemon=True).start()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_KEY = os.getenv("API_KEY")

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}"); sys.stdout.flush()

def analizza_partite():
    url = "https://free-api-live-football-data.p.rapidapi.com/football-current-live"
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "free-api-live-football-data.p.rapidapi.com"
    }
    
    try:
        log("🔍 Ricerca partite live...")
        res = requests.get(url, headers=headers, timeout=15)
        data = res.json()
        
        # Gestione flessibile della risposta
        partite = []
        if isinstance(data.get("response"), list):
            partite = data.get("response")
        elif isinstance(data.get("response"), dict):
            partite = data.get("response", {}).get("matches", [])

        if not partite:
            log("⚠️ Nessuna partita live al momento.")
            return

        msg = "⚽ **GATTONE LIVE REPORT** ⚽\n"
        
        # Prendiamo le prime 10 partite in modo sicuro
        for i, p in enumerate(partite):
            if i >= 10: break
            home = p.get('homeTeam', {}).get('name', 'N/A')
            away = p.get('awayTeam', {}).get('name', 'N/A')
            score = p.get('status', {}).get('scoreStr', 'vs')
            msg += f"\n• {home} **{score}** {away}"

        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
        log(f"✅ Inviate {i+1} partite!")

    except Exception as e:
        log(f"⚠️ Errore durante l'analisi: {e}")

log("🚀 Bot avviato e pronto!")
while True:
    analizza_partite()
    time.sleep(900)
    
