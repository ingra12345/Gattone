import os, requests, time, datetime, random

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
    # Filtro Notte: lavora fino alle 23:00 UTC (01:00 Italia)
    ora = datetime.datetime.now().hour
    if ora < 5 or ora >= 23:
        print(f"🌙 Ore {ora} UTC: Riposo.")
        return

    url = "https://v3.football.api-sports.io/fixtures"
    headers = {"x-apisports-key": API_KEY, "User-Agent": "Mozilla/5.0"}
    
    try:
        # Chiediamo TUTTE le partite live
        res = requests.get(url, headers=headers, params={"live": "all"}, timeout=20)
        fixtures = res.json().get("response", [])
        print(f"⚽ Analizzando {len(fixtures)} partite...")

        for f in fixtures:
            tempo = f['fixture']['status']['elapsed']
            if not tempo or tempo < 5: continue
            
            home = f['teams']['home']['name']
            away = f['teams']['away']['name']
            g_h = f['goals']['home'] or 0
            g_a = f['goals']['away'] or 0
            
            # --- TEST AGGRESSIVO ---
            # Se la partita è tra il minuto 10 e 90 e c'è almeno un attacco, sputa fuori il segnale
            # Questo serve a capire se il bot "vede" i dati
            
            att_p = 0
            stats_list = f.get('statistics', [])
            if stats_list:
                for s in stats_list:
                    for item in s.get('statistics', []):
                        if item['type'] == 'Dangerous Attacks': 
                            valore = str(item['value']).replace('None', '0')
                            att_p += int(valore)
            
            apm = round(att_p / tempo, 2) if tempo > 0 else 0

            # FILTRO TEST: Molto basso (0.50 APM) e nessun obbligo di tiri
            if 10 <= tempo <= 88 and apm >= 0.50:
                msg = (f"📡 **TEST SIGNAL**\n{home} - {away}\n"
                       f"⏰ {tempo}' | 🧨 APM: {apm} | ⚽ Score: {g_h}-{g_a}")
                invia_telegram(msg)
                time.sleep(1)

    except Exception as e:
        print(f"Errore: {e}")

# Messaggio di conferma immediata
invia_telegram("🔥 **TEST AGGRESSIVO AVVIATO**\nSe il bot funziona, ora dovresti ricevere molti segnali.")

while True:
    analizza_partite()
    time.sleep(900 + random.randint(1, 30))
