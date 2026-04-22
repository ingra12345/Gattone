import os, requests, time, sys, threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# Server per Render
threading.Thread(target=lambda: HTTPServer(('0.0.0.0', 10000), type('', (BaseHTTPRequestHandler,), {'do_GET': lambda s: (s.send_response(200), s.end_headers(), s.wfile.write(b"OK"))})).serve_forever(), daemon=True).start()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_KEY = os.getenv("API_KEY")

def analizza():
    # URL preso dal tuo screenshot 1000168889.png
    url = "https://free-api-live-football-data.p.rapidapi.com/football-current-live"
    headers = {"X-RapidAPI-Key": API_KEY, "X-RapidAPI-Host": "free-api-live-football-data.p.rapidapi.com"}
    
    try:
        print(f"[{time.strftime('%H:%M:%S')}] Cerco partite live...")
        res = requests.get(url, headers=headers, timeout=15)
        data = res.json()
        
        if res.status_code != 200:
            print(f"Errore: {data.get('message')}"); return

        partite = data.get("response", {}).get("matches", [])
        if not partite:
            print("Nessuna partita live ora."); return

        msg = "⚽ **GATTONE LIVE** ⚽\n"
        for p in partite[:10]:
            msg += f"\n• {p.get('homeTeam',{}).get('name')} {p.get('status',{}).get('scoreStr')} {p.get('awayTeam',{}).get('name')}"

        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
        print("✅ Inviato!")
    except Exception as e: print(f"Errore: {e}")

while True:
    analizza()
    time.sleep(900)
    
