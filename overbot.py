import os, requests, time, threading, datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

# Server per Render (evita il timeout del servizio)
def run_server():
    class HealthCheckHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Gattone Live")
    server = HTTPServer(('0.0.0.0', 10000), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

# Configurazione Variabili d'Ambiente
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_KEY = os.getenv("API_KEY")

def invia_telegram(testo):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": testo, "parse_mode": "Markdown"})
    except Exception as e:
        print(f"Errore invio Telegram: {e}")

def analizza_partite():
    # --- FILTRO NOTTE (Ora UTC) ---
    # 07:00 - 22:00 UTC corrisponde a circa 09:00 - 00:00 in Italia
    ora = datetime.datetime.now().hour
    if ora < 7 or ora >= 22:
        print(f"🌙 Ore {ora} UTC: Modalità notte. Risparmio quota API.")
        return

    url = "https://v3.football.api-sports.io/fixtures"
    headers = {"x-apisports-key": API_KEY}
    
    try:
        res = requests.get(url, headers=headers, params={"live": "all"}, timeout=15)
        
        # Monitoraggio Crediti nei Log di Render
        rimanenti = res.headers.get('x-ratelimit-requests-remaining', 'N/D')
        print(f"✅ Scansione effettuata. Crediti API rimasti: {rimanenti}")

        if res.status_code != 200:
            print(f"Errore API: {res.status_code}")
            return
        
        data = res.json()
        fixtures = data.get("response", [])
        
        print(f"Analizzando {len(fixtures)} partite in corso...")

        for f in fixtures:
            tempo = f['fixture']['status']['elapsed']
            if not tempo: continue
            
            home = f['teams']['home']['name']
            away = f['teams']['away']['name']
            g_h = f['goals']['home'] or 0
            g_a = f['goals']['away'] or 0
            total_goals = g_h + g_a
            nazione = f['league']['country'].upper()
            lega = f['league']['name']
            
            # Recupero Statistiche (Attacchi Pericolosi e Tiri)
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

            # --- LOGICA FILTRI OTTIMIZZATA ---

            # 1. ALERT OVER 0.5 HT (Min 25-42, 0-0, APM >= 1.1 e 2+ Tiri in porta)
            if 25 <= tempo <= 42 and total_goals == 0 and apm >= 1.1 and tiri_specchio >= 2:
                msg = (f"🎯 **ELITE OVER 0.5 HT**\n\n"
                       f"🌍 {nazione} - {lega}\n"
                       f"⚽️ {home} vs {away}\n"
                       f"⏰ Minuto: {tempo}' | 🧨 AP/m: {apm}\n"
                       f"🥅 Tiri in porta: {tiri_specchio}\n"
                       f"🔥 *Pressione alta nel primo tempo!*")
                invia_telegram(msg)
                time.sleep(2)

            # 2. ALERT OVER FINALE (Min 75-86, gol <= 2, APM >= 1.2 e 5+ Tiri in porta)
            elif 75 <= tempo <= 86 and total_goals <= 2 and apm >= 1.2 and tiri_specchio >= 5:
                msg = (f"🚀 **SUPER OVER FINALE**\n\n"
                       f"🌍 {nazione} - {lega}\n"
                       f"⚽️ {home} vs {away}\n"
                       f"⏰ Minuto: {tempo}' | 🧨 AP/m: {apm}\n"
                       f"🥅 Tiri in porta: {tiri_specchio}\n"
                       f"💰 *Assedio finale rilevato!*")
                invia_telegram(msg)
                time.sleep(2)

    except Exception as e:
        print(f"Errore nel ciclo: {e}")

# Messaggio di avvio
invia_telegram("🤖 **Gattone Online!**\nMonitoraggio attivo (HT 2+ tiri | FT 5+ tiri)\nFrequenza: 12 min")

while True:
    analizza_partite()
    # 720 secondi = 12 minuti. Garantisce stabilità e durata dei crediti.
    time.sleep(720)
