# bot_vs_human_test.py
import os
import asyncio
from telegram import Bot

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHANNEL = os.getenv('TELEGRAM_CHANNEL', '@bursadeneyimlerimiz')

async def test():
    bot = Bot(token=TOKEN)
    
    print("🧪 TEST BAŞLIYOR...")
    print("1. Bot mesajı gönderiliyor...")
    
    # 1. Bot mesajı (şu anki yöntem)
    await bot.send_message(
        chat_id=CHANNEL,
        text='BOT: Simge Kimdir?',
        parse_mode='HTML'
    )
    
    await asyncio.sleep(5)
    print("2. Manuel yazılmış gibi gönderiliyor...")
    
    # 2. "Forwarded" gibi göster (bot gibi görünmesin)
    # Bu biraz hack ama deneyelim
    await bot.send_message(
        chat_id=CHANNEL,
        text='USER: Simge Kimdir?',
        # parse_mode yok, daha doğal
    )
    
    print("\n✅ Test mesajları gönderildi!")
    print("RoseBot hangisine cevap verdi?")

asyncio.run(test())