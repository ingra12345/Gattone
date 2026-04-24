import os, requests, time, sys, threading, datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

# Server per Render (Porta 10000)
threading.Thread(target=lambda: HTTPServer(('0.0.0.0', 10000), type('', (BaseHTTPRequestHandler,), {'do_GET': lambda s: (s.send_response(200), s.end_headers(), s.wfile.write(b"Gattone OK"))})).serve_forever(), daemon=True).start()

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
    # --- FILTRO NOTTE (Risparmio Crediti) ---
    # Lavora dalle 07:00 alle 22:00 UTC (circa 09:00 - 00:00 Italia)
    ora_attuale = datetime.datetime.now().hour
    if ora_attuale < 7 or ora_attuale >= 22:
        print(f"🌙 Ore {ora_attuale}: Modalità notte. Risparmio quota API.")
        return

    url = "https://v3.football.api-sports.io/fixtures"
    headers = {"x-apisports-key": API_KEY}
    
    try:
        # Chiamata API
        res = requests.get(url, headers=headers, params={"live": "all"}, timeout=15)
        
        # Se ricevi errore 429 significa che i crediti sono finiti
        if res.status_code == 429:
            print("⚠️ Quota giornaliera esaurita!")
            return

        if res.status_code != 200: return
        
        fixtures = res.json().get("response", [])
        
        for f in fixtures:
            tempo = f['fixture']['status']['elapsed']
            if not tempo or tempo < 10: continue
            
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

            # --- LOGICA FILTRI (I tuoi settaggi) ---

            # 1. OVER 0.5 HT (Min 25-42, 0-0, APM >= 1.1 e 3+ Tiri in porta)
            if 25 <= tempo <= 42 and total_goals == 0 and apm >= 1.1 and tiri_specchio >= 3:
                msg = f"🎯 **ELITE OVER 0.5 HT**\n\n"
                msg += f"🌍 {nazione} - {lega}\n"
                msg += f"⚽️ {home} vs {away}\n"
                msg += f"⏰ Minuto: {tempo}'\n"
                msg += f"🧨 AP/min: {apm} | 🥅 In Porta: {tiri_specchio}\n\n"
                msg += "🔥 *Filtro: Pressione e precisione!*"
                invia_telegram(msg)
                time.sleep(2)

            # 2. OVER FINALE (Min 75-86, gol <= 2, APM >= 1.2 e 7+ Tiri in porta)
            elif 75 <= tempo <= 86 and total_goals <= 2 and apm >= 1.2 and tiri_specchio >= 7:
                msg = f"🚀 **SUPER OVER FINALE**\n\n"
                msg += f"🌍 {nazione} - {lega}\n"
                msg += f"⚽️ {home} vs {away}\n"
                msg += f"⏰ Minuto: {tempo}'\n"
                msg += f"🧨 AP/min: {apm} | 🥅 In Porta: {tiri_specchio}\n\n"
                msg += "💰 *Filtro: Assedio totale!*"
                invia_telegram(msg)
                time.sleep(2)

    except Exception as e:
        print(f"Errore: {e}")

# AVVIO OGNI 15 MINUTI (900 secondi)
# Questo garantisce 96 chiamate al giorno (Limite Free è 100)
invia_telegram("✅ **Gattone Ripristinato!**\nFiltri: HT (3 tiri) | FT (7 tiri)\nFrequenza: 15 min (Salva-Quota)")

while True:
    analizza_partite()
    time.sleep(900)
