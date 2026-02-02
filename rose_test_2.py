# rosebot_alive_check.py
import os
import asyncio
from telegram import Bot

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHANNEL = os.getenv('TELEGRAM_CHANNEL', '@bursadeneyimlerimiz')

async def check_rosebot_alive():
    """RoseBot canlı mı kontrol et"""
    bot = Bot(token=TOKEN)
    
    print("🔍 ROSE BOT CANLILIK KONTROLÜ")
    print("=" * 40)
    
    # RoseBot'un KESİN çalıştığını bildiğimiz bir komut
    sure_commands = [
        "/start",
        "/help",
        "!help",
        "hello",
        "hi rose",
        "/id",
        "/info",
    ]
    
    for cmd in sure_commands:
        print(f"\n→ {cmd}")
        await bot.send_message(chat_id=CHANNEL, text=cmd)
        await asyncio.sleep(3)
    
    print("\n" + "=" * 40)
    print("❓ RoseBot HİÇBİRİNE cevap verdi mi?")
    print("   - EVET: Filter sorunu")
    print("   - HAYIR: RoseBot bu kanalda YOK/çalışmıyor")

asyncio.run(check_rosebot_alive())