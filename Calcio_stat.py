import requests, time, datetime, sys

API_KEY = '23d4e426cecdd60d8a95af93d8a66205'
TELEGRAM_TOKEN = '8793415569:AAEg57jKGSzGtNC9K7mW3j1Gt0fH0cJM4sU'
CHAT_ID = '165648592'
HEADERS = {'x-apisports-key': API_KEY}

segnalati = []

def invia(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={'chat_id': CHAT_ID, 'text': msg, 'parse_mode': 'Markdown'}, timeout=10)
    except: pass

def scansiona():
    global segnalati
    ora_it = (datetime.datetime.now() + datetime.timedelta(hours=2)).hour
    if ora_it < 7: return
    try:
        r = requests.get("https://v3.football.api-sports.io/fixtures?live=all", headers=HEADERS, timeout=15)
        partite = r.json().get('response', [])
        print(f"Analisi su {len(partite)} match...")
        for m in partite:
            f_id = m['fixture']['id']
            if f_id in segnalati: continue
            elaps = m['fixture']['status'].get('elapsed')
            if not isinstance(elaps, int): continue
            gh = m['goals'].get('home') or 0
            ga = m['goals'].get('away') or 0
            tot = gh + ga
            t_tot = t_p = 0
            for s in m.get('statistics', []):
                for i in s.get('statistics', []):
                    if i['type'] == 'Total Shots': t_tot += int(i['value'] or 0)
                    if i['type'] == 'Shots on Goal': t_p += int(i['value'] or 0)
            h, a, leg = m['teams']['home']['name'], m['teams']['away']['name'], m['league']['name']
            msg = ""
            if 20 <= elaps <= 38:
                if tot == 0 and (t_tot >= 4 or t_p >= 1):
                    msg = f"🐈🔥 *GATTO HT: 0.5 HT*\n🏆 {leg}\n🏟 {h}-{a}\n⏱ {elaps}' | 📊 0-0\n📈 Tiri: {t_tot}/{t_p}"
                elif tot == 1 and (t_tot >= 6 or t_p >= 2):
                    msg = f"🐈🔥 *GATTO HT: 1.5 HT*\n🏆 {leg}\n🏟 {h}-{a}\n⏱ {elaps}' | 📊 {gh}-{ga}\n📈 Tiri: {t_tot}/{t_p}"
            elif 65 <= elaps <= 82 and (t_tot >= 10 or t_p >= 4):
                msg = f"🎯 *GATTO FT: NEXT GOL*\n🏆 {leg}\n🏟 {h}-{a}\n⏱ {elaps}' | 📊 {gh}-{ga}\n💡 Over {float(tot)+0.5}"
            if msg:
                invia(msg)
                segnalati.append(f_id)
    except Exception as e: print(f"Errore: {e}")
    sys.stdout.flush()

if __name__ == "__main__":
    print("--- IL GATTO E ONLINE ---")
    invia("🐈🔥 *IL GATTO* è online!")
    while True:
        scansiona()
        time.sleep(300)
        
