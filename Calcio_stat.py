import os, requests, time, datetime, random

# Variabili caricate da Railway
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
    # Filtro Notte (UTC): dalle 07:00 alle 23:00 (copre tutta la giornata italiana)
    ora = datetime.datetime.now().hour
    if ora < 7 or ora >= 23:
        print(f"🌙 Ore {ora} UTC: Il Gattone dorme per salvare la chiave.")
        return

    url = "https://v3.football.api-sports.io/fixtures"
    
    # User-Agent diverso (simula un iPhone stavolta)
    headers = {
        "x-apisports-key": API_KEY,
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1"
    }
    
    try:
        res = requests.get(url, headers=headers, params={"live": "all"}, timeout=20)
        
        # Log di controllo per te su Railway
        rimanenti = res.headers.get('x-ratelimit-requests-remaining', 'N/D')
        print(f"✅ Chiamata OK. Crediti rimasti: {rimanenti}")

        if res.status_code != 200:
            print(f"Errore API: {res.status_code}")
            return

        fixtures = res.json().get("response", [])
        for f in fixtures:
            tempo = f['fixture']['status']['elapsed']
            if not tempo or tempo < 10: continue
            
            home = f['teams']['home']['name']
            away = f['teams']['away']['name']
            total_goals = (f['goals']['home'] or 0) + (f['goals']['away'] or 0)
            
            # Recupero Statistiche
            att_p = 0; tiri = 0
            stats_list = f.get('statistics', [])
            if stats_list:
                for s in stats_list:
                    for item in s.get('statistics', []):
                        if item['type'] == 'Dangerous Attacks': att_p += int(item['value'] or 0)
                        if item['type'] == 'Shots on Goal': tiri += int(item['value'] or 0)
            
            apm = round(att_p / tempo, 2)

            # --- FILTRI (HT 1+ tiro | FT 3+ tiri) ---
            if 25 <= tempo <= 42 and total_goals == 0 and apm >= 1.0 and tiri >= 1:
                invia_telegram(f"🎯 **ELITE HT**\n{home} vs {away}\nMin: {tempo}' | APM: {apm} | Tiri: {tiri}")
                time.sleep(2)

            elif 75 <= tempo <= 86 and total_goals <= 2 and apm >= 1.1 and tiri >= 3:
                invia_telegram(f"🚀 **SUPER FT**\n{home} vs {away}\nMin: {tempo}' | APM: {apm} | Tiri: {tiri}")
                time.sleep(2)

    except Exception as e:
        print(f"Errore: {e}")

# Messaggio di avvio
invia_telegram("🚂 **Gattone in viaggio su Railway!**\nFrequenza: 18 min\nChiave attiva.")

while True:
    analizza_partite()
    # Aspetta 18 minuti (1080s) + jitter casuale
    attesa = 1080 + random.randint(1, 60)
    time.sleep(attesa)
  
