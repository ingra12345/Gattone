import os, requests, time, sys, threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# Server di vitalità per Render
def run_health_server():
    server_address = ('0.0.0.0', 10000)
    httpd = HTTPServer(server_address, type('', (BaseHTTPRequestHandler,), {
        'do_GET': lambda s: (s.send_response(200), s.end_headers(), s.wfile.write(b"Gattone Online"))
    }))
    httpd.serve_forever()

threading.Thread(target=run_health_server, daemon=True).start()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_KEY = os.getenv("API_KEY")

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}"); sys.stdout.flush()

def invia_telegram(testo):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": testo, "parse_mode": "Markdown"})
    except Exception as e:
        log(f"❌ Errore invio Telegram: {e}")

def analizza_partite():
    # Endpoint ufficiale API-Football v3
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }
    
    try:
        log("🛰️ Recupero match LIVE da API-Football...")
        res = requests.get(url, headers=headers, params={"live": "all"}, timeout=15)
        
        # Gestione Errore 403 (Abbonamento mancante)
        if res.status_code == 403:
            msg_403 = "❌ **ERRORE 403: SOTTOSCRIZIONE MANCANTE**\nDevi attivare il piano Basic ($0) qui:\nhttps://rapidapi.com/api-sports/api/api-football/pricing"
            log(msg_403)
            invia_telegram(msg_403)
            return

        if res.status_code != 200:
            log(f"⚠️ Errore API {res.status_code}: {res.text}")
            return

        data = res.json()
        fixtures = data.get("response", [])
        
        if not fixtures:
            log("⚠️ Nessun match live al momento.")
            return

        report = "⚽ **REPORT LIVE GATTONE** ⚽\n"
        match_count = 0

        for f in fixtures[:20]:
            home = f['teams']['home']['name']
            away = f['teams']['away']['name']
            g_h = f['goals']['home'] or 0
            g_a = f['goals']['away'] or 0
            tempo = f['fixture']['status']['elapsed']
            lega = f['league']['name']
            nazione = f['league']['country']

            # Logica semplice Alert
            alert = ""
            total_goals = g_h + g_a
            if 25 <= tempo <= 40 and total_goals == 0:
                alert = " 🔥 *Alert Over 0.5 HT*"
            elif 70 <= tempo <= 85 and total_goals <= 2:
                alert = " ⚠️ *Alert Over FT*"

            report += f"\n🌍 **{nazione}** ({lega})\n• {home} {g_h}-{g_a} {away} ({tempo}') {alert}\n"
            match_count += 1

        if match_count > 0:
            invia_telegram(report)
            log(f"✅ Report inviato con {match_count} partite.")

    except Exception as e:
        log(f"⚠️ Errore critico: {e}")

# Primo avvio immediato
invia_telegram("🐈‍⬛ **Gattone attivato su API-Football!**\nControllo match live in corso...")
analizza_partite()

# Loop ogni 15 minuti
while True:
    time.sleep(900)
    analizza_partite()
    
