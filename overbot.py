import os
import requests
import time
from datetime import datetime

# Prende i dati dalle impostazioni di Render
API_KEY = os.getenv("API_KEY")
TG_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TGID = os.getenv("TELEGRAM_CHAT_ID")

def controlla():
    # URL specifico per il calcio su RapidAPI
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }
    
    try:
        # Chiediamo TUTTE le partite live
        res = requests.get(url, headers=headers, params={"live": "all"})
        partite = res.json().get("response", [])
        
        print(f"[{datetime.now().strftime('%H:%M')}] Match trovati: {len(partite)}")
        
        if len(partite) > 0:
            # Se ne trova, manda un segnale subito a Telegram
            msg = f"✅ Gattone VEDE {len(partite)} partite live!"
            requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", 
                          json={"chat_id": TGID, "text": msg})
    except Exception as e:
        print(f"Errore: {e}")

while True:
    controlla()
    time.sleep(600) # Un controllo ogni 10 minuti
