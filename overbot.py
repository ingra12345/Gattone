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
    url = "https://v3.football.api-sports.io/fixtures"
    headers = {"x-apisports-key": API_KEY}
    
    try:
        log("🔍 Ricerca segnali operativi...")
        res = requests.get(url, headers=headers, params={"live": "all"}, timeout=15)
        
        if res.status_code == 200:
            data = res.json()
            fixtures = data.get("response", [])
            
            for f in fixtures:
                home = f['teams']['home']['name']
                away = f['teams']['away']['name']
                g_h = f['goals']['home'] or 0
                g_a = f['goals']['away'] or 0
                total = g_h + g_a
                tempo = f['fixture']['status']['elapsed']
                nazione = f['league']['country'].upper()
                lega = f['league']['name']
                
                # --- LOGICA SEGNALI SINGOLI ---
                
                # 1. ALERT OVER 0.5 HT (0-0 dopo il 25')
                if 25 <= tempo <= 42 and total == 0:
                    msg = f"🔥 **SEGNALE OVER 0.5 HT**\n\n"
                    msg += f"🌍 {nazione} - {lega}\n"
                    msg += f"⚽️ {home} vs {away}\n"
                    msg += f"⏰ Minuto: {tempo}'\n"
                    msg += f"📊 Risultato: {g_h}-{g_a}\n\n"
                    msg += f"🎯 *Target: Segnare 1 gol prima della fine del primo tempo.*"
                    invia_telegram(msg)
                    time.sleep(1) # Piccola pausa per non intasare Telegram

                # 2. ALERT OVER FT (Pochi gol nel finale)
                elif 70 <= tempo <= 85 and total <= 2:
                    msg = f"⚠️ **SEGNALE OVER FINALE**\n\n"
                    msg += f"🌍 {nazione} - {lega}\n"
                    msg += f"⚽️ {home} vs {away}\n"
                    msg += f"⏰ Minuto: {tempo}'\n"
                    msg += f"📊 Risultato: {g_h}-{g_a}\n\n"
                    msg += f"🎯 *Target: Almeno un altro gol nel finale.*"
                    invia_telegram(msg)
                    time.sleep(1)

        else:
            log(f"Errore API: {res.status_code}")
            
    except Exception as e:
        log(f"Errore: {e}")

# Avvio e loop
log("Gattone pronto a cacciare segnali singoli!")
while True:
    analizza_partite()
    time.sleep(600) # Controlla ogni 10 minuti (più reattivo)
