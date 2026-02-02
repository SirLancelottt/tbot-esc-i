# test_no_html.py
import os
import asyncio
from telegram import Bot

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHANNEL = os.getenv('TELEGRAM_CHANNEL', '@bursadeneyimlerimiz')

async def test():
    bot = Bot(token=TOKEN)
    
    # HTML OLMADAN gönder
    await bot.send_message(
        chat_id=CHANNEL,
        text='Kedicik Kimdir?',  # parse_mode YOK
    )
    print('✅ HTML olmadan gönderildi')
    
    # 3 saniye bekle
    await asyncio.sleep(3)
    
    # HTML İLE gönder (şu anki yöntem)
    await bot.send_message(
        chat_id=CHANNEL,
        text='<b>Simge Kimdir?</b>',
        parse_mode='HTML'
    )
    print('✅ HTML ile gönderildi')

asyncio.run(test())