import requests, time, sys, datetime

# Configurazione
API_KEY = '962922fc1b4b34437f216732a0f2153c'
TELEGRAM_TOKEN = '8793415569:AAEg57jKGSzGtNC9K7mW3j1Gt0fH0cJM4sU'
CHAT_ID = '-1003710972300'

HEADERS = {'x-apisports-key': API_KEY}

seg_inviati = []

def invia_telegram(messaggio):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={'chat_id': CHAT_ID, 'text': messaggio, 'parse_mode': 'Markdown'}, timeout=10)
    except: pass

def scansione():
    global seg_inviati
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Analisi mercati...")
    try:
        r = requests.get("https://v3.football.api-sports.io/fixtures?live=all", headers=HEADERS, timeout=15)
        res = r.json()
        partite = res.get('response', [])
        print(f"Match Live monitorati: {len(partite)}")

        for m in partite:
            f_id = m['fixture']['id']
            if f_id in seg_inviati: continue
            minuto = m['fixture']['status'].get('elapsed')
            if not minuto: continue

            sh, sa = (m['goals'].get('home') or 0), (m['goals'].get('away') or 0)
            tot_g = sh + sa
            h, a = m['teams']['home']['name'], m['teams']['away']['name']
            lg = m['league']['name']
            
            t_tot, t_port = 0, 0
            stats_list = m.get('statistics', [])
            if stats_list:
                for team_stats in stats_list:
                    for s in team_stats.get('statistics', []):
                        if s['type'] == 'Total Shots': t_tot += (int(s['value']) if s['value'] else 0)
                        if s['type'] == 'Shots on Goal': t_port += (int(s['value']) if s['value'] else 0)

            # Filtri meno rigidi
            if 15 <= minuto <= 45 and tot_g <= 1:
                if t_tot >= 3 or t_port >= 1:
                    invia_telegram(f"⚽️ *GATTO HT*\n🏆 {lg}\n🏟 {h} - {a}\n⏱ {minuto}' | {sh}-{sa}")
                    seg_inviati.append(f_id)
            elif 60 <= minuto <= 85:
                if t_tot >= 8 or t_port >= 3:
                    invia_telegram(f"🔥 *GATTO FINALE*\n🏆 {lg}\n🏟 {h} - {a}\n⏱ {minuto}' | {sh}-{sa}")
                    seg_inviati.append(f_id)
    except Exception as e:
        print(f"Errore: {e}")
    sys.stdout.flush()

invia_telegram("🚀 *GATTO LIVE ATTIVO SU RENDER*")
while True:
    scansione()
    time.sleep(180)
  
