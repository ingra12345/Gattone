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
    # Filtro Orario (UTC): 07:00 - 23:00
    ora = datetime.datetime.now().hour
    if ora < 7 or ora >= 23:
        print(f"🌙 Ore {ora} UTC: Modalità riposo.")
        return

    url = "https://v3.football.api-sports.io/fixtures"
    headers = {
        "x-apisports-key": API_KEY,
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1"
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
            
            # Statistiche
            att_p = 0; tiri = 0
            stats_list = f.get('statistics', [])
            if stats_list:
                for s in stats_list:
                    for item in s.get('statistics', []):
                        if item['type'] == 'Dangerous Attacks': att_p += int(item['value'] or 0)
                        if item['type'] == 'Shots on Goal': tiri += int(item['value'] or 0)
            
            apm = round(att_p / tempo, 2)

            # --- FILTRI RITARATI (Più probabili) ---
            
            # HT: Min 25-42, 0-0, APM 0.8+, Almeno 1 tiro in porta
            if 25 <= tempo <= 42 and total_goals == 0 and apm >= 0.8 and tiri >= 1:
                msg = (f"🎯 **ELITE HT**\n{home} - {away}\n"
                       f"⏰ {tempo}' | 🧨 APM: {apm} | 🥅 Tiri: {tiri}")
                invia_telegram(msg)
                time.sleep(1)

            # FT: Min 75-86, Gol totali <= 2, APM 0.9+, Almeno 2 tiri in porta
            elif 75 <= tempo <= 86 and total_goals <= 2 and apm >= 0.9 and tiri >= 2:
                msg = (f"🚀 **SUPER FT**\n{home} - {away}\n"
                       f"⏰ {tempo}' | 🧨 APM: {apm} | 🥅 Tiri: {tiri}")
                invia_telegram(msg)
                time.sleep(1)

    except Exception as e:
        print(f"Errore: {e}")

# Avvio
invia_telegram("🔄 **Gattone aggiornato!**\nFiltri più sensibili attivati.\nA caccia di segnali...")

while True:
    analizza_partite()
    # 18 minuti di attesa + jitter
    time.sleep(1080 + random.randint(1, 30))
