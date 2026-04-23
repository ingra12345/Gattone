import os, requests, time, sys, threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# Server di vitalità per Render
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
    # URL CORRETTO per Football Live Score (emir12)
    # Proviamo l'endpoint generico delle fixture che è il più stabile
    url = "https://football-live-score2.p.rapidapi.com/matches/fixtures"
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "football-live-score2.p.rapidapi.com"
    }
    
    try:
        log("🔍 Analisi in corso...")
        # Cerchiamo i match di oggi per essere sicuri di ricevere dati
        oggi = time.strftime("%Y-%m-%d")
        res = requests.get(url, headers=headers, params={"date": oggi}, timeout=15)
        
        if res.status_code != 200:
            errore_msg = f"❌ Errore API {res.status_code}\nURL: {url}\nControlla se l'endpoint è attivo."
            log(errore_msg)
            invia_telegram(errore_msg)
            return

        data = res.json()
        # Gestione flessibile dei dati (alcune API usano 'data', altre 'response', altre la lista diretta)
        matches = data.get("data", []) if isinstance(data, dict) else data
        
        if not matches:
            log("⚠️ Nessun match trovato per oggi.")
            return

        msg = "⚽ **GATTONE REPORT** ⚽\n"
        for m in matches[:15]:
            home = m.get('home_team', {}).get('name', 'Home')
            away = m.get('away_team', {}).get('name', 'Away')
            status = m.get('status', {}).get('type', 'Ora non nota')
            msg += f"\n• {home} vs {away}\n  Stato: {status}"

        invia_telegram(msg)
        log("✅ Report inviato con successo!")

    except Exception as e:
        log(f"⚠️ Errore critico: {e}")
        invia_telegram(f"⚠️ Errore nel codice: {e}")

# Primo tentativo immediato all'avvio
invia_telegram("🚀 **Bot avviato!** Provo a leggere i dati...")
analizza_partite()

while True:
    time.sleep(900)
    analizza_partite()
    
