import os, requests, time, sys, threading
from http.server import BaseHTTPRequestHandler, HTTPServer

threading.Thread(target=lambda: HTTPServer(('0.0.0.0', 10000), type('', (BaseHTTPRequestHandler,), {'do_GET': lambda s: (s.send_response(200), s.end_headers(), s.wfile.write(b"Gattone OK"))})).serve_forever(), daemon=True).start()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_KEY = os.getenv("API_KEY")

def invia_telegram(testo):
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": testo, "parse_mode": "Markdown"})

def analizza_partite():
    url = "https://v3.football.api-sports.io/fixtures"
    headers = {"x-apisports-key": API_KEY}
    
    try:
        res = requests.get(url, headers=headers, params={"live": "all"}, timeout=15)
        if res.status_code != 200: return
        
        fixtures = res.json().get("response", [])
        
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
            
            # --- RECUPERO STATISTICHE ---
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

            # --- FILTRI RICHIESTI ---

            # 1. OVER 0.5 HT (Min 25-42, 0-0, APM >= 1.1 E ALMENO 3 TIRI IN PORTA)
            if 25 <= tempo <= 42 and total_goals == 0 and apm >= 1.1 and tiri_specchio >= 3:
                msg = f"🎯 **ELITE OVER 0.5 HT**\n\n"
                msg += f"🌍 {nazione} - {lega}\n"
                msg += f"⚽️ {home} vs {away}\n"
                msg += f"⏰ Minuto: {tempo}'\n"
                msg += f"🧨 AP/min: {apm} | 🥅 In Porta: {tiri_specchio}\n\n"
                msg += "🔥 *Filtro: Massima pressione, 3+ tiri nello specchio!*"
                invia_telegram(msg)
                time.sleep(2)

            # 2. OVER FINALE (Min 75-86, total gol <= 2, APM >= 1.2 E ALMENO 7 TIRI IN PORTA)
            elif 75 <= tempo <= 86 and total_goals <= 2 and apm >= 1.2 and tiri_specchio >= 7:
                msg = f"🚀 **SUPER OVER FINALE**\n\n"
                msg += f"🌍 {nazione} - {lega}\n"
                msg += f"⚽️ {home} vs {away}\n"
                msg += f"⏰ Minuto: {tempo}'\n"
                msg += f"🧨 AP/min: {apm} | 🥅 In Porta: {tiri_specchio}\n\n"
                msg += "💰 *Filtro: Assedio totale, 7+ tiri nello specchio!*"
                invia_telegram(msg)
                time.sleep(2)

    except Exception as e:
        print(f"Errore: {e}")

while True:
    analizza_partite()
    time.sleep(600)            stats_list = f.get('statistics', [])
            if stats_list:
                for s in stats_list:
                    for item in s.get('statistics', []):
                        if item['type'] == 'Dangerous Attacks':
                            attacchi_p += int(item['value'] or 0)
                        if item['type'] == 'Shots on Goal':
                            tiri_specchio += int(item['value'] or 0)
            
            apm = round(attacchi_p / tempo, 2)

            # --- FILTRI ELITE ---

            # 1. OVER 0.5 HT (Min 25-42, 0-0, APM > 1.1 E almeno 1 tiro in porta)
            if 25 <= tempo <= 42 and total_goals == 0 and apm >= 1.1 and tiri_specchio >= 1:
                msg = f"🎯 **BOMBA OVER 0.5 HT**\n\n"
                msg += f"🌍 {nazione} - {lega}\n"
                msg += f"⚽️ {home} vs {away}\n"
                msg += f"⏰ Minuto: {tempo}'\n"
                msg += f"🧨 AP/min: {apm} | 🥅 In Porta: {tiri_specchio}\n\n"
                msg += "🔥 *Filtro: Pressione altissima e mira centrata!*"
                invia_telegram(msg)
                time.sleep(2)

            # 2. OVER FINALE (Min 75-86, total gol <= 2, APM > 1.2 E almeno 4 tiri in porta totali)
            elif 75 <= tempo <= 86 and total_goals <= 2 and apm >= 1.2 and tiri_specchio >= 4:
                msg = f"🚀 **ASSEDIO FINALE - OVER**\n\n"
                msg += f"🌍 {nazione} - {lega}\n"
                msg += f"⚽️ {home} vs {away}\n"
                msg += f"⏰ Minuto: {tempo}'\n"
                msg += f"🧨 AP/min: {apm} | 🥅 In Porta: {tiri_specchio}\n\n"
                msg += "💰 *Filtro: Partita caldissima, tiri costanti.*"
                invia_telegram(msg)
                time.sleep(2)

    except Exception as e:
        print(f"Errore: {e}")

while True:
    analizza_partite()
    time.sleep(600)
