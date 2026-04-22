import os
import requests
import time
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# --- SERVER PER MANTENERE RENDER ATTIVO ---
class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self): 
        self.send_response(200); self.end_headers(); self.wfile.write(b"Gattone Online")
    def do_HEAD(self): 
        self.send_response(200); self.end_headers()

threading.Thread(target=lambda: HTTPServer(('0.0.0.0', 10000), HealthCheck).serve_forever(), daemon=True).start()

# --- CONFIGURAZIONE ---
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_KEY = os.getenv("API_KEY")

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")
    sys.stdout.flush()

def invia_telegram(testo):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": testo, "parse_mode": "Markdown"}
    try:
        r
    try:
        log("🔍 Controllo partite live...")
        res = requests.get(url, headers=headers, timeout=15)
        data = res.json()
        partite = data.get("response", [])
        
        if not partite or not isinstance(partite, list):
            log("Nessuna partita live trovata (Lista vuota).")
            # Mandiamo un segnale di vita ogni ora anche se non ci sono partite
            return

        messaggio = f"⚽ **GATTONE LIVE** ⚽\nPartite: {len(partite)}\n"
        for p in partite[:10]:
            home = p.get('homeTeam', {}).get('name', 'Casa')
            away = p.get('awayTeam', {}).get('name', 'Fuori')
            score = p.get('status', {}).get('scoreStr', '0-0')
            messaggio += f"\n• {home} **{score}** {away}"
        
        invia_telegram(messaggio)

    except Exception as e:
        log(f"⚠️ Errore API: {e}")

# --- TEST IMMEDIATO ALL'AVVIO ---
log("🚀 Avvio test di connessione...")
if invia_telegram("🔔 **GATTONE ONLINE!**\nSe leggi questo, il collegamento con Telegram è OK. Ora cerco le partite ogni 15 minuti."):
    log("✅ Test Telegram superato!")
else:
    log("❌ Test Telegram FALLITO. Controlla TOKEN e CHAT_ID su Render!")

while True:
    analizza_partite()
    time.sleep(900) # 15 minuti
