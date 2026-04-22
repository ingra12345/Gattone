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
    # URL ESATTO preso dal tuo screenshot di RapidAPI
    url = "https://free-api-live-football-data.p.rapidapi.com/football-current-live"
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "free-api-live-football-data.p.rapidapi.com"
    }
    
    try:
        log("🔍 Ricerca partite in corso...")
        res = requests.get(url, headers=headers, timeout=15)
        data = res.json()
        
        if res.status_code != 200:
            log(f"❌ Errore API: {data.get('message')}")
            return

        # Questa API restituisce i dati dentro 'response'
        partite = data.get("response", [])
        
        if not partite:
            log("⚠️ Nessuna partita live in questo momento.")
            return

        messaggio = "⚽ **GATTONE LIVE REPORT** ⚽\n"
        # Prendiamo le prime 10 partite live
        for p in partite[:10]:
            home = p.get('homeTeam', {}).get('name', 'N/A')
            away = p.get('awayTeam', {}).get('name', 'N/A')
            score = p.get('status', {}).get('scoreStr', 'vs')
            messaggio += f"\n• {home} **{score}** {away}"

        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": messaggio, "parse_mode": "Markdown"})
        log(f"✅ Inviate {len(partite[:10])} partite!")

    except Exception as e:
        log(f"⚠️ Errore: {e}")

log("🚀 Bot avviato correttamente!")
while True:
    analizza_partite()
    time.sleep(900) # Controlla ogni 15 minuti
