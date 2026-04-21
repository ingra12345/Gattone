import os
import requests
import time
from datetime import datetime, timedelta

# Configurazione dalle variabili d'ambiente di Render
API_KEY = os.getenv("API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def invia_telegram(messaggio):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": messaggio, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

def analizza_partite():
    # URL AGGRESSIVO: Prende TUTTE le partite live nel mondo
    url = "https://v3.football.api-sports.io/fixtures?live=all"
    headers = {"x-apisports-key": API_KEY}
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        fixtures = data.get("response", [])
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Analisi mercati...")
        print(f"Match Live monitorati: {len(fixtures)}")

        for match in fixtures:
            home = match['teams']['home']['name']
            away = match['teams']['away']['name']
            minuto = match['fixture']['status']['elapsed']
            
            # FILTRO: Minuto tra 15 e 85
            if 15 <= minuto <= 85:
                # Invia un messaggio di prova per ogni partita trovata così siamo sicuri che funziona!
                msg = f"⚽ *Match Identificato*\n{home} vs {away}\nMinuto: {minuto}'"
                invia_telegram(msg)
                
    except Exception as e:
        print(f"Errore: {e}")

# Ciclo infinito
while True:
    analizza_partite()
    time.sleep(600) # Controlla ogni 10 minuti
        partite = res.get('response', [])
        print(f"Match Live: {len(partite)}")

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

            if 15 <= minuto <= 45 and tot_g <= 1:
                if t_tot >= 3 or t_port >= 1:
                    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
                                  data={'chat_id': CHAT_ID, 'text': f"⚽️ *GATTO HT*\n🏆 {lg}\n🏟 {h} - {a}\n⏱ {minuto}' | {sh}-{sa}", 'parse_mode': 'Markdown'})
                    seg_inviati.append(f_id)
            elif 60 <= minuto <= 85:
                if t_tot >= 8 or t_port >= 3:
                    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
                                  data={'chat_id': CHAT_ID, 'text': f"🔥 *GATTO FINALE*\n🏆 {lg}\n🏟 {h} - {a}\n⏱ {minuto}' | {sh}-{sa}", 'parse_mode': 'Markdown'})
                    seg_inviati.append(f_id)
    except Exception as e: print(f"Errore: {e}")
    sys.stdout.flush()

threading.Thread(target=run_finto_server, daemon=True).start()

while True:
    scansione()
    time.sleep(600) # 10 minuti
