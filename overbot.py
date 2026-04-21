import os
import requests
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# --- CONFIGURAZIONE ---
API_KEY = os.getenv("API_KEY")
TG_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TGID = os.getenv("TELEGRAM_CHAT_ID")

# --- SERVER PER RENDER (EVITA ERRORI ROSSI) ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Gattone is Alive")

def run_health_server():
    server = HTTPServer(('0.0.0.0', 10000), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_health_server, daemon=True).start()

# --- FUNZIONE DI ANALISI ---
def analizza():
    # Verifichiamo se le variabili sono caricate
    if not API_KEY or not TG_TOKEN:
        print("❌ ERRORE: Variabili API_KEY o TELEGRAM_BOT_TOKEN mancanti su Render!")
        return

    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }
    
    try:
        # Chiamata API per i match LIVE
        res = requests.get(url, headers=headers, params={"live": "all"}, timeout=10)
        data = res.json()
        
        #
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }
    
    try:
        # Chiediamo tutte le partite attualmente in corso (LIVE)
        response = requests.get(url, headers=headers, params={"live": "all"})
        data = response.json()
        fixtures = data.get("response", [])
        
        orario = datetime.now().strftime('%H:%M')
        print(f"[{orario}] Scansione effettuata. Match trovati: {len(fixtures)}")

        if len(fixtures) > 0:
            # Se trova partite, manda un messaggio di conferma solo per la prima (TEST)
            primo_match = fixtures[0]
            casa = primo_match['teams']['home']['name']
            trasferta = primo_match['teams']['away']['name']
            
            test_msg = f"✅ Gattone Online!\nSta monitorando {len(fixtures)} partite.\nEsempio: {casa} vs {trasferta}"
            
            # Invio a Telegram
            requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", 
                          json={"chat_id": TGID, "text": test_msg})
            
    except Exception as e:
        print(f"Errore durante l'analisi: {e}")

# --- CICLO INFINITO ---
print("Gattone avviato con successo...")
while True:
    analizza_partite()
    # Controlla ogni 10 minuti per non finire i crediti RapidAPI (100 al giorno)
    time.sleep(600)
