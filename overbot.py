import os, requests, time, sys, threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# Server per mantenere vivo il bot su Render (Porta 10000)
def run_health_server():
    server_address = ('0.0.0.0', 10000)
    httpd = HTTPServer(server_address, type('', (BaseHTTPRequestHandler,), {
        'do_GET': lambda s: (s.send_response(200), s.end_headers(), s.wfile.write(b"Gattone OK"))
    }))
    httpd.serve_forever()

threading.Thread(target=run_health_server, daemon=True).start()

# Caricamento Variabili d'Ambiente
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_KEY = os.getenv("API_KEY")

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}"); sys.stdout.flush()

def analizza_partite():
    # URL per API-Football (V3)
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }
    
    # Per il test, prendiamo tutte le partite di oggi
    oggi = time.strftime("%Y-%m-%d")
    params = {"date": oggi}
    
    try:
        log(f"🔍 API-Football: Recupero palinsesto del {oggi}...")
        res = requests.get(url, headers=headers, params=params, timeout=15)
        
        if res.status_code != 200:
            log(f"❌ Errore API ({res.status_code}): {res.text}")
            return

        data = res.json()
        fixtures = data.get("response", [])
        
        if not fixtures:
            log(f"⚠️ Nessun match trovato per la data {oggi}. Controlla la sottoscrizione Basic.")
            return

        # Costruzione del messaggio
        msg = f"⚽ **PALINSESTO DEL GIORNO ({oggi})** ⚽\n"
        match_count = 0

        # Prendiamo i primi 15 match per non superare i limiti di Telegram
        for f in fixtures[:15]:
            nazione = f['league']['country']
            lega = f['league']['name']
            home = f['teams']['home']['name']
            away = f['teams']['away']['name']
            # Estraiamo l'orario (formato ISO: 2026-04-23T15:00:00+00:00)
            orario = f['fixture']['date'].split('T')[1][:5]

            msg += f"\n🌍 **{nazione}** ({lega})\n"
            msg += f"• {home} vs {away} - Ore {orario}\n"
            match_count += 1

        # Invio a Telegram
        telegram_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        response = requests.post(telegram_url, json={
            "chat_id": CHAT_ID, 
            "text": msg, 
            "parse_mode": "Markdown"
        })
        
        if response.status_code == 200:
            log(f"✅ Inviato report con {match_count} partite su Telegram!")
        else:
            log(f"❌ Errore invio Telegram: {response.text}")

    except Exception as e:
        log(f"⚠️ Errore critico nel loop: {e}")

# Messaggio di avvio immediato
log("🚀 Bot avviato! Invio messaggio di test...")
analizza_partite()

# Loop infinito ogni 15 minuti
while True:
    time.sleep(900)
    analizza_partite()
    
