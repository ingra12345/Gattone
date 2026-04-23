import os, requests, time, sys, threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# Server di vitalità per Render
threading.Thread(target=lambda: HTTPServer(('0.0.0.0', 10000), type('', (BaseHTTPRequestHandler,), {'do_GET': lambda s: (s.send_response(200), s.end_headers(), s.wfile.write(b"Gattone OK"))})).serve_forever(), daemon=True).start()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_KEY = os.getenv("API_KEY")

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}"); sys.stdout.flush()

def controllo_totale():
    # Proviamo a connetterci all'API corretta
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }
    
    try:
        log("🛰️ Test di connessione con la tua nuova API_KEY...")
        # Proviamo a vedere se ci sono match live
        res = requests.get(url, headers=headers, params={"live": "all"}, timeout=15)
        
        if res.status_code == 200:
            data = res.json()
            fixtures = data.get("response", [])
            log(f"✅ CONNESSIONE RIUSCITA! Trovati {len(fixtures)} match live.")
            
            msg = "🚀 **IL GATTONE È ATTIVO!**\n\n"
            if not fixtures:
                msg += "Connessione OK, ma al momento non ci sono match live nel database."
            else:
                msg += f"Ho trovato {len(fixtures)} partite in diretta.\nEcco le prime 5:\n"
                for f in fixtures[:5]:
                    home = f['teams']['home']['name']
                    away = f['teams']['away']['name']
                    msg += f"\n• {home} vs {away}"
            
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
        
        elif res.status_code == 403:
            log("❌ ERRORE 403: Devi ancora attivare il piano gratuito su RapidAPI!")
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": "❌ **ERRORE 403**\nLa tua chiave è corretta, ma devi cliccare su 'Subscribe' (piano $0) nella pagina di API-Football su RapidAPI!"})
        
        else:
            log(f"⚠️ Errore {res.status_code}: {res.text}")

    except Exception as e:
        log(f"⚠️ Errore critico: {e}")

# Avvio immediato
controllo_totale()

while True:
    time.sleep(900) # Controllo ogni 15 minuti
    controllo_totale()
    
