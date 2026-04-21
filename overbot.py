import os
import requests
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# 1. SERVER DI SERVIZIO (PORTA 10000)
class SimpleServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"BOT ATTIVO")

def run_on_port_10000():
    server = HTTPServer(('0.0.0.0', 10000), SimpleServer)
    server.serve_forever()

threading.Thread(target=run_on_port_10000, daemon=True).start()

# 2. VARIABILI CARICATE DA RENDER
API_KEY = os.getenv("API_KEY")
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

print("--- IL BOT SI STA SVEGLIANDO ---")

def controllo():
    print(f"[{time.strftime('%H:%M:%S')}] Sto provando a contattare l'API...")
    
    url = "https://free-api-live-football-data.p.rapidapi.com/football-current-live"
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "free-api-live-football-data.p.rapidapi.com"
    }
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
        dati = r.json()
        match = dati.get("response", [])
        
        print(f"RISULTATO: Trovati {len(match)} match live.")
        
        # MANDIAMO UN MESSAGGIO FORZATO A TELEGRAM
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                      json={"chat_id": CHAT_ID, "text": f"Gattone Online! Match: {len(match)}"})
    except Exception as e:
        print(f"ERRORE DURANTE IL TEST: {e}")

# Ciclo infinito ogni 30 secondi (solo per ora, per vedere se scrive)
while True:
    controllo()
    time.sleep(30)
    
