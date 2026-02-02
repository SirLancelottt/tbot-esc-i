# rose_test_c.py
import os
import asyncio
from telegram import Bot

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHANNEL = os.getenv('TELEGRAM_CHANNEL', '@bursadeneyimlerimiz')

async def test_quoted_messages():
    """Tırnak içinde mesajları test et"""
    bot = Bot(token=TOKEN)
    
    print("🧪 TIRNAK İÇİNDE MESAJ TESTİ")
    print("=" * 40)
    
    test_cases = [
        # Orijinal
        "Gerçek Bayanlar Nerde?",
        # Tırnak içinde
        '"Gerçek Bayanlar Nerde?"',
        # Çift tırnak
        '“Gerçek Bayanlar Nerde?”',
        # Tek tırnak
        "'Gerçek Bayanlar Nerde?'",
        # Köşeli parantez
        "[Gerçek Bayanlar Nerde?]",
        # Normal
        "Kedicik Kimdir?",
        # Tırnaklı
        '"Kedicik Kimdir?"',
    ]
    
    for i, message in enumerate(test_cases, 1):
        print(f"\n{i}. Gönderiliyor: {message}")
        
        try:
            await bot.send_message(
                chat_id=CHANNEL,
                text=message,
                parse_mode=None  # HTML yok
            )
            
            # RoseBot'un cevap vermesi için bekle
            await asyncio.sleep(3)
            
        except Exception as e:
            print(f"   Hata: {e}")
    
    print("\n" + "=" * 40)
    print("✅ Tüm testler gönderildi!")
    print("Hangi formata RoseBot cevap verdi?")

# Hemen çalıştır
asyncio.run(test_quoted_messages())