import os, requests, time, threading, datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

# Server per Render (evita il timeout)
def run_server():
    class HealthCheckHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Gattone RapidAPI Live")
    server = HTTPServer(('0.0.0.0', 10000), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_KEY = os.getenv("API_KEY") # Qui devi mettere la X-RapidAPI-Key

def invia_telegram(testo):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": testo, "parse_mode": "Markdown"})
    except: pass

def analizza_partite():
    # Filtro Notte (UTC)
    ora = datetime.datetime.now().hour
    if ora < 7 or ora >= 22:
        print(f"🌙 Modalità notte attiva (Ora UTC: {ora})")
        return

    # URL SPECIFICO PER RAPIDAPI
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    
    # HEADERS SPECIFICI PER RAPIDAPI
        headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }

    
    try:
        res = requests.get(url, headers=headers, params={"live": "all"}, timeout=15)
        
        # Controllo crediti RapidAPI (spesso chiamati 'requests')
        rem = res.headers.get('X-RateLimit-Requests-Remaining', 'N/D')
        print(f"✅ Scansione RapidAPI. Crediti rimasti: {rem}")

        if res.status_code != 200:
            print(f"Errore RapidAPI: {res.status_code}")
            return
        
        fixtures = res.json().get("response", [])
        
        for f in fixtures:
            tempo = f['fixture']['status']['elapsed']
            if not tempo: continue
            
            home = f['teams']['home']['name']
            away = f['teams']['away']['name']
            total_goals = (f['goals']['home'] or 0) + (f['goals']['away'] or 0)
            
            attacchi_p = 0
            tiri_specchio = 0
            stats_list = f.get('statistics', [])
            
            if stats_list:
                for s in stats_list:
                    for item in s.get('statistics', []):
                        if item['type'] == 'Dangerous Attacks': attacchi_p += int(item['value'] or 0)
                        if item['type'] == 'Shots on Goal': tiri_specchio += int(item['value'] or 0)
            
            apm = round(attacchi_p / tempo, 2)

            # Filtri HT (2 tiri) e FT (5 tiri)
            if 25 <= tempo <= 42 and total_goals == 0 and apm >= 1.1 and tiri_specchio >= 2:
                invia_telegram(f"🎯 **RAPID-HT**\n{home} vs {away}\nAPM: {apm} | Tiri: {tiri_specchio}")
                time.sleep(1)

            elif 75 <= tempo <= 86 and total_goals <= 2 and apm >= 1.2 and tiri_specchio >= 5:
                invia_telegram(f"🚀 **RAPID-FT**\n{home} vs {away}\nAPM: {apm} | Tiri: {tiri_specchio}")
                time.sleep(1)

    except Exception as e:
        print(f"Errore: {e}")

invia_telegram("🔄 **Gattone switchato su RapidAPI!**\nFrequenza: 12 min")

while True:
    analizza_partite()
    time.sleep(720) # 12 minuti
