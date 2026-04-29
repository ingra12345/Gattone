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
    # FILTRO NOTTE (UTC): Lavora dalle 05:00 alle 23:00 (copre 07:00 - 01:00 in Italia)
    # Impostato a 5 per evitare che il bot si spenga per errore la mattina presto.
    ora = datetime.datetime.now().hour
    if ora < 5 or ora >= 23:
        print(f"🌙 Ore {ora} UTC: Il Gattone dorme per risparmiare crediti.")
        return

    url = "https://v3.football.api-sports.io/fixtures"
    headers = {
        "x-apisports-key": API_KEY,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        res = requests.get(url, headers=headers, params={"live": "all"}, timeout=20)
        rimanenti = res.headers.get('x-ratelimit-requests-remaining', 'N/D')
        print(f"✅ Chiamata OK. Crediti rimasti: {rimanenti}")

        if res.status_code != 200:
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
            
            # Recupero statistiche
            att_p = 0; tiri = 0
            stats_list = f.get('statistics', [])
            if stats_list:
                for s in stats_list:
                    for item in s.get('statistics', []):
                        if item['type'] == 'Dangerous Attacks': att_p += int(item['value'] or 0)
                        if item['type'] == 'Shots on Goal': tiri += int(item['value'] or 0)
            
            apm = round(att_p / tempo, 2)

            # --- FILTRI RITARATI (Più sensibili) ---
            
            # HT: 0-0, Min 25-42, APM 0.8+, Almeno 1 tiro in porta
            if 25 <= tempo <= 42 and total_goals == 0 and apm >= 0.8 and tiri >= 1:
                msg = (f"🎯 **ELITE HT**\n{home} - {away}\n"
                       f"⏰ {tempo}' | 🧨 APM: {apm} | 🥅 Tiri: {tiri}")
                invia_telegram(msg)
                time.sleep(1)

            # FT: Gol totali <= 2, Min 75-86, APM 0.9+, Almeno 2 tiri in porta
            elif 75 <= tempo <= 86 and total_goals <= 2 and apm >= 0.9 and tiri >= 2:
                msg = (f"🚀 **SUPER FT**\n{home} - {away}\n"
                       f"⏰ {tempo}' | 🧨 APM: {apm} | 🥅 Tiri: {tiri}")
                invia_telegram(msg)
                time.sleep(1)

    except Exception as e:
        print(f"Errore: {e}")

# Avvio
invia_telegram("☀️ **Gattone Operativo!**\nFiltri sensibili e pausa 15m attivi.")

while True:
    analizza_partite()
    # Pausa di 15 minuti (900 secondi) + piccolo ritardo casuale per sicurezza
    time.sleep(900 + random.randint(1, 30))
    
