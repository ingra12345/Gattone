import os, requests, time, threading, datetime, random
from http.server import BaseHTTPRequestHandler, HTTPServer

# --- SERVER PER RENDER (Evita lo spegnimento del servizio) ---
def run_server():
    class HealthHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Gattone Anti-Ban 3.1 Online")
    server = HTTPServer(('0.0.0.0', 10000), HealthHandler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

# --- CONFIGURAZIONE VARIABILI ---
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_KEY = os.getenv("API_KEY")

def invia_telegram(testo):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": testo, "parse_mode": "Markdown"})
    except Exception as e:
        print(f"Errore Telegram: {e}")

def analizza_partite():
    # --- PROTEZIONE 1: FILTRO ORARIO ---
    # Monitora dalle 09:00 alle 00:30 italiane (07:00 - 22:30 UTC)
    ora_utc = datetime.datetime.now().hour
    if ora_utc < 7 or ora_utc >= 23:
        print(f"🌙 Ore {ora_utc} UTC: Modalità risparmio per non farsi notare.")
        return

    url = "https://v3.football.api-sports.io/fixtures"
    
    # --- PROTEZIONE 2: MASCHERAMENTO BROWSER ---
    headers = {
        "x-apisports-key": API_KEY,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        res = requests.get(url, headers=headers, params={"live": "all"}, timeout=15)
        
        # Log per monitorare i crediti
        rimanenti = res.headers.get('x-ratelimit-requests-remaining', 'N/D')
        print(f"✅ Chiamata effettuata. Crediti API rimasti: {rimanenti}")

        if res.status_code != 200:
            print(f"Errore API: {res.status_code}")
            return

        data = res.json()
        fixtures = data.get("response", [])
        
        print(f"🧐 Analisi in corso su {len(fixtures)} partite...")

        for f in fixtures:
            tempo = f['fixture']['status']['elapsed']
            if not tempo or tempo < 5: continue
            
            home = f['teams']['home']['name']
            away = f['teams']['away']['name']
            g_h = f['goals']['home'] or 0
            g_a = f['goals']['away'] or 0
            total_goals = g_h + g_a
            
            # Statistiche Live
            attacchi_p = 0
            tiri_specchio = 0
            stats_list = f.get('statistics', [])
            
            if stats_list:
                for s in stats_list:
                    for item in s.get('statistics', []):
                        if item['type'] == 'Dangerous Attacks':
                            attacchi_p += int(item['value'] or 0)
                        if item['type'] == 'Shots on Goal':
                            tiri_specchio += int(item['value'] or 0)
            
            apm = round(attacchi_p / tempo, 2)

            # --- FILTRI AGGIORNATI (Più sensibili per lunedì sera) ---
            
            # ALERT HT: Min 25-42, 0-0, APM >= 1.0, Almeno 1 Tiro in porta
            if 25 <= tempo <= 42 and total_goals == 0 and apm >= 1.0 and tiri_specchio >= 1:
                msg = (f"🎯 **ELITE HT**\n\n"
                       f"⚽️ {home} vs {away}\n"
                       f"⏰ Minuto: {tempo}'\n"
                       f"🧨 AP/m: {apm} | 🥅 Tiri: {tiri_specchio}\n"
                       f"🔥 *Pressione rilevata!*")
                invia_telegram(msg)
                time.sleep(2) # Pausa tra messaggi

            # ALERT FT: Min 75-86, Gol totali <= 2, APM >= 1.1, Almeno 3 Tiri in porta
            elif 75 <= tempo <= 86 and total_goals <= 2 and apm >= 1.1 and tiri_specchio >= 3:
                msg = (f"🚀 **SUPER FINALE**\n\n"
                       f"⚽️ {home} vs {away}\n"
                       f"⏰ Minuto: {tempo}'\n"
                       f"🧨 AP/m: {apm} | 🥅 Tiri: {tiri_specchio}\n"
                       f"💰 *Assedio finale!*")
                invia_telegram(msg)
                time.sleep(2)

    except Exception as e:
        print(f"Errore nel ciclo: {e}")

# --- AVVIO E GESTIONE TEMPI (PROTEZIONE 3: ANTI-PATTERN) ---
invia_telegram("🤖 **Gattone 3.1 Anti-Ban Online**\nFrequenza: 15min + Random\nFiltri: HT 1+ tir | FT 3+ tiri")

while True:
    analizza_partite()
    # Aspetta 15 minuti (900s) + un ritardo casuale fino a 60 secondi
    attesa = 900 + random.randint(1, 60)
    print(f"⏳ Prossima scansione tra {attesa} secondi...")
    time.sleep(attesa)
    
