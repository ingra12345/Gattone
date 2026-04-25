import os, requests, time, sys, threading, datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

# Server per Render
threading.Thread(target=lambda: HTTPServer(('0.0.0.0', 10000), type('', (BaseHTTPRequestHandler,), {'do_GET': lambda s: (s.send_response(200), s.end_headers(), s.wfile.write(b"Gattone OK"))})).serve_forever(), daemon=True).start()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_KEY = os.getenv("API_KEY")

def invia_telegram(testo):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": testo, "parse_mode": "Markdown"})
    except: pass

def analizza_partite():
    # FILTRO NOTTE (Ora UTC: dalle 07 alle 22 -> 09-00 in Italia)
    ora_attuale = datetime.datetime.now().hour
    if ora_attuale < 7 or ora_attuale >= 22:
        print("🌙 Notte: Risparmio chiamate...")
        return

    url = "https://v3.football.api-sports.io/fixtures"
    headers = {"x-apisports-key": API_KEY}
    
    try:
        res = requests.get(url, headers=headers, params={"live": "all"}, timeout=15)
        if res.status_code != 200: 
            print(f"Errore API: {res.status_code}")
            return
        
        fixtures = res.json().get("response", [])
        for f in fixtures:
            tempo = f['fixture']['status']['elapsed']
            if not tempo: continue
            
            home = f['teams']['home']['name']
            away = f['teams']['away']['name']
            total_goals = (f['goals']['home'] or 0) + (f['goals']['away'] or 0)
            
            # Recupero statistiche
            attacchi_p = 0
            tiri_specchio = 0
            stats_list = f.get('statistics', [])
            if stats_list:
                for s in stats_list:
                    for item in s.get('statistics', []):
                        if item['type'] == 'Dangerous Attacks': attacchi_p += int(item['value'] or 0)
                        if item['type'] == 'Shots on Goal': tiri_specchio += int(item['value'] or 0)
            
            apm = round(attacchi_p / tempo, 2)

            # --- FILTRI HT 3 TIRI | FT 7 TIRI ---
            if 25 <= tempo <= 42 and total_goals == 0 and apm >= 1.1 and tiri_specchio >= 3:
                invia_telegram(f"🎯 **ELITE HT (3+ Tiri)**\n\n⚽️ {home} vs {away}\n⏰ {tempo}' | 🧨 AP/m: {apm} | 🥅 Porta: {tiri_specchio}")
                time.sleep(2)

            elif 75 <= tempo <= 86 and total_goals <= 2 and apm >= 1.2 and tiri_specchio >= 7:
                invia_telegram(f"🚀 **SUPER FT (7+ Tiri)**\n\n⚽️ {home} vs {away}\n⏰ {tempo}' | 🧨 AP/m: {apm} | 🥅 Porta: {tiri_specchio}")
                time.sleep(2)

    except Exception as e:
        print(f"Errore: {e}")

# AVVIO OGNI 15 MINUTI (900 secondi) = 96 chiamate al giorno (Limite 100)
invia_telegram("🆕 **Nuovo Account Attivo!**\nFiltri: 3 HT / 7 FT\nFrequenza: 15 min")

while True:
    analizza_partite()
    time.sleep(900)
