import os, requests, time, sys, threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# Server per Render
threading.Thread(target=lambda: HTTPServer(('0.0.0.0', 10000), type('', (BaseHTTPRequestHandler,), {'do_GET': lambda s: (s.send_response(200), s.end_headers(), s.wfile.write(b"Gattone OK"))})).serve_forever(), daemon=True).start()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_KEY = os.getenv("API_KEY")

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}"); sys.stdout.flush()

def analizza_partite():
    # URL per Football Live Score (emir12/UltimateApps)
    url = "https://football-live-score2.p.rapidapi.com/matches/live"
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "football-live-score2.p.rapidapi.com"
    }
    
    try:
        log("🔍 Analisi match live (Nuova API)...")
        res = requests.get(url, headers=headers, timeout=15)
        
        if res.status_code != 200:
            log(f"❌ Errore API {res.status_code}")
            return

        data = res.json()
        # In questa API i match sono spesso dentro 'data' o direttamente nella lista
        matches = data.get("data", []) if isinstance(data, dict) else data
        
        if not matches:
            log("⚠️ Nessun match live trovato ora.")
            return

        msg = "⚽ **GATTONE LIVE REPORT** ⚽\n"
        count = 0

        for m in matches[:20]:
            # Adattamento nomi campi basato sul RAW dell'API emir12
            home = m.get('home_team', {}).get('name', 'Home')
            away = m.get('away_team', {}).get('name', 'Away')
            score = m.get('score', '0-0')
            tempo = m.get('minute', '?')
            lega = m.get('league', {}).get('name', 'Lega')

            msg += f"\n🏆 {lega}\n• {home} **{score}** {away} ({tempo}')\n"
            count += 1

        if count > 0:
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": msg})
            log(f"✅ Inviato report con {count} match.")

    except Exception as e:
        log(f"⚠️ Errore: {e}")

# Test immediato
analizza_partite()

while True:
    time.sleep(900)
    analizza_partite()
    
