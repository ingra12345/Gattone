import os, requests, time, sys, threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# Server per Render
threading.Thread(target=lambda: HTTPServer(('0.0.0.0', 10000), type('', (BaseHTTPRequestHandler,), {'do_GET': lambda s: (s.send_response(200), s.end_headers(), s.wfile.write(b"Gattone OK"))})).serve_forever(), daemon=True).start()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
# Usa la chiave b6f93beeda6a4863c395ed78bdda0673 che si vede nello screenshot
API_KEY = os.getenv("API_KEY")

def invia_telegram(testo):
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": testo, "parse_mode": "Markdown"})

def analizza_partite():
    # NUOVO URL DIRETTO (Senza RapidAPI)
    url = "https://v3.football.api-sports.io/fixtures"
    
    headers = {
        "x-apisports-key": API_KEY  # Nome chiave cambiato per connessione diretta
    }
    
    try:
        print("🔍 Controllo match live su API-SPORTS...")
        res = requests.get(url, headers=headers, params={"live": "all"}, timeout=15)
        
        if res.status_code == 200:
            data = res.json()
            fixtures = data.get("response", [])
            
            if not fixtures:
                return

            msg = "⚽ **GATTONE LIVE (DIRETTO)** ⚽\n"
            for f in fixtures[:15]:
                home = f['teams']['home']['name']
                away = f['teams']['away']['name']
                score = f"{f['goals']['home']}-{f['goals']['away']}"
                tempo = f['fixture']['status']['elapsed']
                
                # Alert Over
                if tempo > 25 and (f['goals']['home'] + f['goals']['away']) == 0:
                    msg += f"\n🔥 **{home} vs {away}** ({tempo}') - *Alert 0.5 HT*"
                else:
                    msg += f"\n• {home} {score} {away} ({tempo}')"
            
            invia_telegram(msg)
        else:
            print(f"Errore: {res.status_code}")
            
    except Exception as e:
        print(f"Errore critico: {e}")

invia_telegram("🚀 **Gattone collegato direttamente ad API-SPORTS!**")
analizza_partite()

while True:
    time.sleep(900)
    analizza_partite()
    
