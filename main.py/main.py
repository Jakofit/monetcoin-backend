
from fastapi import FastAPI, Request
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import telegram
import os

app = FastAPI()

# Config
BOT_TOKEN = os.getenv("BOT_TOKEN")
SHEET_NAME = os.getenv("SHEET_NAME", "monetcoin_reward")
WORKSHEET_NAME = os.getenv("WORKSHEET_NAME", "Sheet1")
bot = telegram.Bot(token=BOT_TOKEN)

# Setup Google Sheets API
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("monetcoinbot-creds.json", scope)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).worksheet(WORKSHEET_NAME)

@app.post("/claim")
async def claim_poin(request: Request):
    headers = request.headers
    user_ip = request.client.host
    user_agent = headers.get("user-agent", "")
    referrer = headers.get("referer", "")

    # Simpan ke Google Sheet
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([timestamp, user_ip, user_agent, referrer, 1])

    # Kirim pesan ke Telegram user jika ada tg_id
    data = await request.json()
    tg_id = data.get("tg_id")
    if tg_id:
        try:
            bot.send_message(chat_id=tg_id, text="🎉 Kamu baru saja mendapat 1 poin dari MonetCoin Reward!")
        except Exception as e:
            return {"status": "error", "message": str(e)}

    return {"status": "success", "message": "Poin berhasil diklaim!"}
