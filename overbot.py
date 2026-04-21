import os
import requests
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# Server per Render (Porta 10000)
class RenderHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Gattone Operativo")
    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

threading.Thread(target=lambda: HTTPServer(('0.0.0.0', 10000), RenderHandler).serve_forever(), daemon=True).start()

# Configurazione
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_KEY = os.getenv("API_KEY")

print(f"--- AVVIO BOT SU CHAT {CHAT_ID} ---")

def analizza():
    url = "https://free-api-live-football-data.p.rapidapi.com/football-current-live"
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "free-api-live-football-data.p.rapidapi.com"
    }
    
    try:
        # 1. Recupero Dati
        res = requests.get(url, headers=headers, timeout=10)
        data = res.json()
        partite = data.get("response", [])
        
        # 2. Invio Testo a Telegram
        testo = f"⚽ **Gattone Update**\nPartite live trovate: {len(partite)}"
        
        # Se ci sono partite, aggiungile al messaggio
        if len(partite) > 0:
            for p in partite[:5]: # Vediamo le prime 5
                home = p.get('homeTeam', {}).get('name', 'Casa')
                away = p.get('awayTeam', {}).get('name', 'Fuori')
                score = p.get('status', {}).get('scoreStr', '0-0')
                testo += f"\n• {home} {score} {away}"

        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                      json={"chat_id": CHAT_ID, "text": testo, "parse_mode": "Markdown"})
        
        print(f"Inviato a Telegram! Match: {len(partite)}")

    except Exception as e:
        print(f"Errore: {e}")

# Ciclo ogni 10 minuti
while True:
    analizza()
    time.sleep(600)
    
