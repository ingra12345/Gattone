import os, requests, time, threading, datetime, random
from http.server import BaseHTTPRequestHandler, HTTPServer

# Server per mantenere vivo il servizio su Render
def run_server():
    class HealthHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Gattone Anti-Ban Online")
    server = HTTPServer(('0.0.0.0', 10000), HealthHandler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

# Configurazione variabili (Assicurati di averle su Render)
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_KEY = os.getenv("API_KEY")

def invia_telegram(testo):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": testo, "parse_mode": "Markdown"})
    except:
        pass

def analizza_partite():
    # --- PROTEZIONE 1: FILTRO ORARIO ---
    # Lavora dalle 09:00 alle 23:59 ora italiana (circa 07:00-22:00 UTC)
    ora_utc = datetime.datetime.now().hour
    if ora_utc < 7 or ora_utc >= 22:
        print(f"🌙 Ore {ora_utc} UTC: Modalità risparmio attiva.")
        return

    url = "https://v3.football.api-sports.io/fixtures"
    
    # --- PROTEZIONE 2: USER-AGENT (Mascheramento da Browser) ---
    headers = {
        "x-apisports-key": API_KEY,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        res = requests.get(url, headers=headers, params={"live": "all"}, timeout=15)
        
        # Monitoraggio crediti residui
        rimanenti = res.headers.get('x-ratelimit-requests-remaining', 'N/D')
        print(f"✅ Chiamata effettuata. Crediti API rimasti: {rimanenti}")

        if res.status_code == 403 or res.status_code == 429:
            print("⚠️ Attenzione: API sospesa o crediti finiti.")
            return

        fixtures = res.json().get("response", [])
        
        for f in fixtures:
            tempo = f['fixture']['status']['elapsed']
            if not tempo or tempo < 10: continue
            
            home = f['teams']['home']['name']
            away = f['teams']['away']['name']
            g_h = f['goals']['home'] or 0
            g_a = f['goals']['away'] or 0
            total_goals = g_h + g_a
            
            # Recupero Statistiche
            attacchi_p = 0
            tiri_specchio = 0
            stats_list = f.get('statistics', [])
            
            if stats_list:
                for s in stats_list:
                    for item in s.get('statistics', []):
                        if item['type'] == 'Dangerous Attacks': attacchi_p += int(item['value'] or 0)
                        if item['type'] == 'Shots on Goal': tiri_specchio += int(item['value'] or 0)
            
            apm = round(attacchi_p / tempo, 2)

            # --- I TUOI FILTRI (HT 2 tiri | FT 5 tiri) ---
            
            # OVER 0.5 HT
            if 25 <= tempo <= 42 and total_goals == 0 and apm >= 1.1 and tiri_specchio >= 2:
                msg = f"🎯 **ELITE HT**\n{home} - {away}\n⏰ {tempo}' | 🧨 AP/m: {apm} | 🥅 Porta: {tiri_specchio}"
                invia_telegram(msg)
                time.sleep(2)

            # OVER FINALE
            elif 75 <= tempo <= 86 and total_goals <= 2 and apm >= 1.2 and tiri_specchio >= 5:
                msg = f"🚀 **SUPER FT**\n{home} - {away}\n⏰ {tempo}' | 🧨 AP/m: {apm} | 🥅 Porta: {tiri_specchio}"
                invia_telegram(msg)
                time.sleep(2)

    except Exception as e:
        print(f"Errore: {e}")

# AVVIO CON RITARDO CASUALE (Protezione 3: Anti-Pattern)
invia_telegram("🤖 **Gattone 3.0 Anti-Ban Attivo!**")

while True:
    analizza_partite()
    # Aspetta circa 15 minuti (900s) + un ritardo casuale tra 1 e 40 secondi
    ritardo_variabile = 900 + random.randint(1, 40)
    time.sleep(ritardo_variabile)
