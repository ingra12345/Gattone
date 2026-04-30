from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import requests
import os

TOKEN = os.getenv('TOKEN')
CHAT_ID = int(os.getenv('CHAT_ID'))

is_active = False

async def start(update, context):
    keyboard = [[InlineKeyboardButton("✅ ACCENDI", callback_data='on'),
                 InlineKeyboardButton("❌ SPEGNI", callback_data='off')]]
    await update.message.reply_text("🤖 Bot Over Primo Tempo", reply_markup=InlineKeyboardMarkup(keyboard))

async def button(update, context):
    global is_active
    query = update.callback_query
    await query.answer()

    if query.data == 'on':
        is_active = True
        await query.edit_message_text("✅ Bot **ACCESO**")
    else:
        is_active = False
        await query.edit_message_text("❌ Bot **SPENTO**")

async def check_live(context):
    if not is_active:
        return
    try:
        r = requests.get("https://api.sofascore.com/api/v1/sport/football/events/live", 
                        headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        
        for match in r.json().get("events", []):
            status = match.get("status", {})
            minute = status.get("minute") or 0
            if "1st half" not in status.get("description", "").lower():
                continue
                
            hg = match.get("homeScore", {}).get("current", 0)
            ag = match.get("awayScore", {}).get("current", 0)
            total = hg + ag
            
            if (total == 0 and minute >= 18) or (total == 1 and minute >= 12):
                emoji = "🔴" if total == 0 else "🟡"
                over = "0.5" if total == 0 else "1.5"
                home = match.get("homeTeam", {}).get("name", "")
                away = match.get("awayTeam", {}).get("name", "")
                country = match.get("category", {}).get("name", "")
                league = match.get("tournament", {}).get("name", "")
                
                testo = f"{emoji} Over {over} Primo Tempo\n{country} - {league}\n{home} - {away}\nRisultato: {hg}-{ag} | {minute}'\n→ Scommetti: Over {over} HT"
                await context.bot.send_message(chat_id=CHAT_ID, text=testo)
    except:
        pass

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.job_queue.run_repeating(check_live, interval=35, first=10)
    
    print("Bot avviato con polling")
    app.run_polling()

if __name__ == "__main__":
    main()            minute = status.get("minute") or 0
            if "1st half" not in status.get("description", "").lower():
                continue
                
            hg = match.get("homeScore", {}).get("current", 0)
            ag = match.get("awayScore", {}).get("current", 0)
            total = hg + ag
            
            if (total == 0 and minute >= 18) or (total == 1 and minute >= 12):
                emoji = "🔴" if total == 0 else "🟡"
                over = "0.5" if total == 0 else "1.5"
                home = match.get("homeTeam", {}).get("name", "")
                away = match.get("awayTeam", {}).get("name", "")
                country = match.get("category", {}).get("name", "")
                league = match.get("tournament", {}).get("name", "")
                
                testo = f"{emoji} Over {over} Primo Tempo\n{country} - {league}\n{home} - {away}\nRisultato: {hg}-{ag} | {minute}'\nScommetti: Over {over} HT"
                await context.bot.send_message(chat_id=CHAT_ID, text=testo)
    except:
        pass

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    
    # Job per controllare le partite ogni 35 secondi
    app.job_queue.run_repeating(check_live, interval=35, first=10)
    
    # Webhook
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", 8443)),
        url_path=TOKEN,
        webhook_url=f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/{TOKEN}"
    )

if __name__ == "__main__":
    main()
