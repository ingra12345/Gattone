import os, requests, time, sys, threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# Server per Render
threading.Thread(target=lambda: HTTPServer(('0.0.0.0', 10000), type('', (BaseHTTPRequestHandler,), {'do_GET': lambda s: (s.send_response(200), s.end_headers(), s.wfile.write(b"Gattone OK"))})).serve_forever(), daemon=True).start()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_KEY = os.getenv("API_KEY")

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}"); sys.stdout.flush()

def invia_telegram(testo):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": testo, "parse_mode": "Markdown"})

def analizza_partite():
    # URL basato sul tuo test RAW riuscito
    url = "https://football-live-score2.p.rapidapi.com/matches/results"
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "football-live-score2.p.rapidapi.com"
    }
    
    try:
        log("🔍 Recupero risultati odierni...")
        # Parametri richiesti dall'API di emir12
        oggi = time.strftime("%Y-%m-%d")
        params = {"date": oggi, "edition": "en"}
        
        res = requests.get(url, headers=headers, params=params, timeout=15)
        
        if res.status_code != 200:
            invia_telegram(f"❌ Errore {res.status_code} su endpoint results.")
            return

        data = res.json()
        # L'API emir12 restituisce spesso i match in una lista 'data'
        matches = data.get("data", []) if isinstance(data, dict) else data
        
        if not matches:
            log("⚠️ Nessun match trovato per oggi.")
            return

        msg = "⚽ **GATTONE REPORT (Risultati)** ⚽\n"
        count = 0
        for m in matches[:15]:
            home = m.get('home_team', {}).get('name', 'N/A')
            away = m.get('away_team', {}).get('name', 'N/A')
            score = m.get('score', '0-0')
            msg += f"\n• {home} **{score}** {away}"
            count += 1

        if count > 0:
            invia_telegram(msg)
            log(f"✅ Inviate {count} partite.")

    except Exception as e:
        log(f"⚠️ Errore: {e}")

# Notifica di riavvio
invia_telegram("🔄 **Bot aggiornato!** Provo l'endpoint 'results'...")
analizza_partite()

while True:
    time.sleep(900)
    analizza_partite()
    
