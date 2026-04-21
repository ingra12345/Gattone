import requests, time, sys, datetime, os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# Configurazione
API_KEY = 'b366105bf42831dcfda69ad2df55442a'
TELEGRAM_TOKEN = '8793415569:AAEg57jKGSzGtNC9K7mW3j1Gt0fH0cJM4sU'
CHAT_ID = '-1003710972300'
HEADERS = {'x-apisports-key': API_KEY}

seg_inviati = []

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Gattone e attivo')

def run_finto_server():
    port = int(os.environ.get("PORT", 8080))
    httpd = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    httpd.serve_forever()

def scansione():
    global seg_inviati
    # Orario italiano (UTC+2)
    ora_it = (datetime.datetime.utcnow() + datetime.timedelta(hours=2)).hour
    
    if ora_it < 7:
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Gattone dorme (Ora: {ora_it})")
        return

    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Analisi mercati...")
    try:
        r = requests.get("https://v3.football.api-sports.io/fixtures?live=all", headers=HEADERS, timeout=15)
        res = r.json()
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
