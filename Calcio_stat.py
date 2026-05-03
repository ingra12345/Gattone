import requests, time, datetime, sys

# --- CONFIGURAZIONE ---
API_KEY = '23d4e426cecdd60d8a95af93d8a66205'
TELEGRAM_TOKEN = '8793415569:AAEg57jKGSzGtNC9K7mW3j1Gt0fH0cJM4sU'
CHAT_ID = '165648592' 

HEADERS = {'x-apisports-key': API_KEY}
PROXIES = {'http': 'http://proxy.server:3128', 'https': 'http://proxy.server:3128'}

segnalati_ht = []
segnalati_ft = []

def invia_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={'chat_id': CHAT_ID, 'text': msg, 'parse_mode': 'Markdown'}, proxies=PROXIES, timeout=10)
    except: pass

def scansione_totale():
    global segnalati_ht, segnalati_ft
    ora_server = datetime.datetime.now()
    ora_italiana = (ora_server + datetime.timedelta(hours=1)).hour
    
    if ora_italiana < 7: return

    try:
        r = requests.get("https://v3.football.api-sports.io/fixtures?live=all", headers=HEADERS, proxies=PROXIES, timeout=15)
        res = r.json()
        partite = res.get('response', [])
        now_it = (datetime.datetime.now() + datetime.timedelta(hours=1)).strftime('%H:%M')
        print(f"[{now_it}] Analisi su {len(partite)} partite...")
        
        for m in partite:
            f_id = m['fixture']['id']
            minuto = m['fixture']['status'].get('elapsed')
            if not isinstance(minuto, int): continue
            
            sh, sa = m['goals'].get('home') or 0, m['goals'].get('away') or 0
            tot_g = sh + sa
            
            stats_list = m.get('statistics', [])
            t_tot = t_port = 0
            for s in stats_list:
                for item in s.get('statistics', []):
                    val = int(item['value'] or 0)
                    if item['type'] == 'Total Shots': t_tot += val
                    if item['type'] == 'Shots on Goal': t_port += val

            home, away = m['teams']['home']['name'], m['teams']['away']['name']
            league = m['league']['name']
            
            # --- HT (Filtri abbassati a 4 tiri totali per test) ---
            if 20 <= minuto <= 38 and f_id not in segnalati_ht:
                msg_ht = ""
                if tot_g == 0 and (t_tot >= 4 or t_port >= 1):
                    msg_ht = f"🐈🔥 *GATTO HT: 0.5 HT*\n🏆 {league}\n🏟 {home}-{away}\n⏱ {minuto}' | 📊 0-0\n📈 Tiri: {t_tot}/{t_port}"
                elif tot_g == 1 and (t_tot >= 6 or t_port >= 2):
                    msg_ht = f"🐈🔥 *GATTO HT: 1.5 HT*\n🏆 {league}\n🏟 {home}-{away}\n⏱ {minuto}' | 📊 {sh}-{sa}\n📈 Tiri: {t_tot}/{t_port}"
                if msg_ht:
                    invia_telegram(msg_ht)
                    segnalati_ht.append(f_id)

            # --- FT (Filtri abbassati a 10 tiri totali) ---
            if 65 <= minuto <= 82 and f_id not in segnalati_ft:
                if t_tot >= 10 or t_port >= 4:
                    targ = float(tot_g) + 0.5
                    msg_ft = f"🎯 *GATTO FT: NEXT GOL*\n🏆 {league}\n🏟 {home}-{away}\n⏱ {minuto}' | 📊 {sh}-{sa}\n📈 Tiri: {t_tot}/{t_port}\n💡 Over {targ}"
                    invia_telegram(msg_ft)
                    segnalati_ft.append(f_id)
                
    except Exception as e:
        print(f"Errore: {e}")
    sys.stdout.flush()

print("--- IL GATTO CHE SCOTTA È RIPARTITO ---")
sys.stdout.flush()
invia_telegram("🐈🔥 *IL GATTO CHE SCOTTA* è ripartito. Controllo orario ITA ok!")

while True:
    scansione_totale()
    time.sleep(300)
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
