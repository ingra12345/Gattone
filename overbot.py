import os
import requests
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# --- CONFIGURAZIONE VARIABILI ---
# Questi dati vengono letti direttamente da Render (sezione Environment)
API_KEY = os.getenv("API_KEY")
TG_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TGID = os.getenv("TELEGRAM_CHAT_ID")

# --- TRUCCO PER RENDER (EVITA L'ERRORE ROSSO) ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Gattone e' attivo e sta monitorando!")

def run_server():
    # Render usa la porta 10000 di default
    server = HTTPServer(('0.0.0.0', 10000), SimpleHTTPRequestHandler)
    print("Server di keep-alive avviato sulla porta 10000")
    server.serve_forever()

# Avvia il server in un thread separato per non bloccare il bot
threading.Thread(target=run_server, daemon=True).start()

# --- LOGICA DEL BOT ---
def analizza_partite():
    # URL ufficiale per il calcio su RapidAPI
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    
    headers = {
        "X-RapidAPI-Key": API_KEY,
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
