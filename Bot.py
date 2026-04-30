from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import requests

TOKEN = '8795405468:AAHoL3xqAhdfHnkPbS0iiXeNUcmUNaVmE3A'
CHAT_ID = -1003801422569   # ← Cambia con il tuo vero chat ID

is_active = False

async def start(update, context):
    keyboard = [[InlineKeyboardButton("✅ ACCENDI", callback_data='on'),
                 InlineKeyboardButton("❌ SPEGNI", callback_data='off')]]
    await update.message.reply_text("Bot Over Primo Tempo", reply_markup=InlineKeyboardMarkup(keyboard))

async def button(update, context):
    global is_active
    query = update.callback_query
    await query.answer()

    if query.data == 'on':
        is_active = True
        await query.edit_message_text("✅ Bot ACCESO")
    else:
        is_active = False
        await query.edit_message_text("❌ Bot SPENTO")

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
                testo = f"{emoji} Over {over} HT\n{country}\n{home} - {away}\nMinuto: {minute}' | {hg}-{ag}"
                await context.bot.send_message(chat_id=CHAT_ID, text=testo)
    except:
        pass

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.job_queue.run_repeating(check_live, interval=35, first=5)

print("Bot avviato - Scrivi /start")
app.run_polling()
