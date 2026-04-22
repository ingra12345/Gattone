import os, requests, time, sys, threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# Server per Render (Health Check)
threading.Thread(target=lambda: HTTPServer(('0.0.0.0', 10000), type('', (BaseHTTPRequestHandler,), {'do_GET': lambda s: (s.send_response(200), s.end_headers(), s.wfile.write(b"OK"))})).serve_forever(), daemon=True).start()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_KEY = os.getenv("API_KEY")

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}"); sys.stdout.flush()

def analizza_partite():
    # FILTRO NOTTE (00:00 - 07:00)
    ora_attuale = int(time.strftime("%H"))
    if 0 <= ora_attuale < 7:
        log("🌙 Il Gattone dorme (Filtro Notte attivo).")
        return

    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    headers = {"X-RapidAPI-Key": API_KEY, "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"}
    
    try:
        log("🔍 Analisi match live e ricerca Over...")
        res = requests.get(url, headers=headers, params={"live": "all"}, timeout=15)
        data = res.json()
        fixtures = data.get("response", [])
        
        if not fixtures:
            log("⚠️ Nessun match live al momento."); return

        msg = "⚽ **GATTONE LIVE REPORT** ⚽\n"
        count = 0

        for f in fixtures[:25]: # Analizziamo un range più ampio
            home = f['teams']['home']['name']
            away = f['teams']['away']['name']
            nazione = f['league']['country']
            lega = f['league']['name']
            status = f['fixture']['status']['short']
            elaps = f['fixture']['status']['elapsed']
            
            # Gol attuali
            g_h = f['goals']['home'] if f['goals']['home'] is not None else 0
            g_a = f['goals']['away'] if f['goals']['away'] is not None else 0
            total_goals = g_h + g_a
            
            # Risultato HT
            score_ht = f.get('score', {}).get('halftime', {})
            ht_h = score_ht.get('home') if score_ht.get('home') is not None else 0
            ht_a = score_ht.get('away') if score_ht.get('away') is not None else 0

            # Logica Alert
            alert = ""
            if status == "1H" and elaps > 20 and total_goals == 0:
                alert = "⚠️ *Puntare Over 0.5 HT?*"
            elif status == "2H" and elaps > 65 and total_goals <= 1:
                alert = "🔥 *Puntare Over FT?*"

            # Costruzione riga messaggio
            riga = f"\n🌍 **{nazione}** ({lega})\n"
            riga += f"• {home} **{g_h}-{g_a}** {away} | {elaps}'"
            
            if status == "HT": riga += " [INTERVALLO]"
            if status == "2H": riga += f" (HT: {ht_h}-{ht_a})"
            if alert: riga += f"\n  {alert}"
            
            msg += riga + "\n"
            count += 1

        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
        log(f"✅ Inviato report con {count} partite.")

    except Exception as e:
        log(f"⚠️ Errore: {e}")

log("🚀 Bot API-Football (Paesi/HT/FT) Online!")
while True:
    analizza_partite()
    # 900 secondi = 15 minuti (96 chiamate al giorno)
    time.sleep(900)
    
