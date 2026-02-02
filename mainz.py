#!/usr/bin/env python3
"""
ÇALIŞAN TELEGRAM BOT - MESAJ GÖNDERİR
"""

import os
import sys
import time
import schedule
import logging
import asyncio
import pytz
from datetime import datetime
from telegram import Bot

# ==================== AYARLAR ====================
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHANNEL = os.getenv('TELEGRAM_CHANNEL', '@bursadeneyimlerimiz')

# ==================== LOG ====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
log = logging.getLogger()

# ==================== MESAJ LİSTESİ ====================
MESSAGES = [
    {'time': '09:00', 'message': '⏰ <b>GÜNAYDIN!</b>\n\nBugün harika bir gün olacak! ☀️'},
    {'time': '12:00', 'message': '☀️ <b>ÖĞLE VAKTİ</b>\n\nAra verip kendinize iyi bakın! 🍽️'},
    {'time': '14:15', 'message': 'Gerçek Bayanlar Nerde?'},
    {'time': '14:30', 'message': 'Kedicik Kimdir?'},
    {'time': '14:45', 'message': 'Simge Kimdir?'},
    {'time': '15:00', 'message': 'Çağla Kimdir?'},
    {'time': '15:15', 'message': 'Gerçek Bayanlar Nerde?'},
    {'time': '15:30', 'message': 'Kedicik Kimdir?'},
    {'time': '15:45', 'message': 'Simge Kimdir?'},
    {'time': '16:00', 'message': 'Çağla Kimdir?'},
    {'time': '16:15', 'message': 'Gerçek Bayanlar Nerde?'},
    {'time': '16:30', 'message': 'Kedicik Kimdir?'},
    {'time': '16:45', 'message': 'Simge Kimdir?'},
    {'time': '17:00', 'message': 'Çağla Kimdir?'},
    {'time': '17:15', 'message': 'Gerçek Bayanlar Nerde?'},
    {'time': '17:30', 'message': 'Kedicik Kimdir?'},
    {'time': '17:45', 'message': 'Simge Kimdir?'},
    {'time': '18:00', 'message': 'Çağla Kimdir?'},
    {'time': '18:15', 'message': 'Gerçek Bayanlar Nerde?'},
    {'time': '18:30', 'message': 'Kedicik Kimdir?'},
    {'time': '18:45', 'message': 'Simge Kimdir?'},
    {'time': '19:00', 'message': 'Çağla Kimdir?'},
    {'time': '19:15', 'message': 'Gerçek Bayanlar Nerde?'},
    {'time': '19:30', 'message': 'Kedicik Kimdir?'},
    {'time': '19:45', 'message': 'Simge Kimdir?'},
    {'time': '20:00', 'message': 'Çağla Kimdir?'},
    {'time': '20:00', 'message': '🌆 <b>AKŞAM VAKTİ</b>\n\nGünün yorgunluğunu atma zamanı! 🏡'},
    {'time': '23:59', 'message': '🌙 <b>İYİ GECELER</b>\n\nYarın daha güzel bir gün olacak! ✨'}
]

# ==================== FONKSİYONLAR ====================
async def send_message_async(text):
    """Mesaj gönder"""
    try:
        bot = Bot(token=TOKEN)
        await bot.send_message(
            chat_id=CHANNEL,
            text=text,
            parse_mode='HTML'
        )
        log.info(f"✅ Gönderildi: {text[:40]}...")
        return True
    except Exception as e:
        log.error(f"❌ Gönderme hatası: {e}")
        return False

def send_message(text):
    """Senkron wrapper"""
    try:
        asyncio.run(send_message_async(text))
    except Exception as e:
        log.error(f"Gönderme hatası: {e}")

def tr_to_utc(tr_time):
    """TR saati → UTC"""
    try:
        tr_tz = pytz.timezone('Europe/Istanbul')
        
        # Saati parçala
        hour, minute = map(int, tr_time.split(':'))
        
        # Bugünün tarihi
        today = datetime.now().date()
        
        # TRT zamanı oluştur
        tr_datetime = tr_tz.localize(
            datetime(today.year, today.month, today.day, hour, minute, 0)
        )
        
        # UTC'ye çevir
        utc_datetime = tr_datetime.astimezone(pytz.UTC)
        return utc_datetime.strftime('%H:%M')
        
    except Exception as e:
        log.error(f"Zaman çevirme hatası: {e}")
        return tr_time

def setup_schedule():
    """Zamanlamaları ayarla"""
    log.info("⏰ Zamanlamalar ayarlanıyor...")
    
    for item in MESSAGES:
        tr_time = item['time']
        message = item['message']
        utc_time = tr_to_utc(tr_time)
        
        schedule.every().day.at(utc_time).do(
            send_message, 
            message_text=message
        )
        
        log.info(f"   {tr_time} TRT → {utc_time} UTC")
    
    log.info(f"✅ {len(MESSAGES)} mesaj zamanlandı")
    return schedule

async def startup_test():
    """Başlangıç testi"""
    try:
        bot = Bot(token=TOKEN)
        
        # Bot bilgisi
        me = await bot.get_me()
        log.info(f"🤖 Bot: @{me.username}")
        
        # Kanal bilgisi
        chat = await bot.get_chat(CHANNEL)
        log.info(f"📢 Kanal: {chat.title}")
        
        # Test mesajı
        await bot.send_message(
            chat_id=CHANNEL,
            text='🚀 <b>BOT YENİDEN BAŞLATILDI</b>\n\nZamanlanmış mesajlar aktif! ✅',
            parse_mode='HTML'
        )
        log.info("✅ Test mesajı gönderildi")
        return True
        
    except Exception as e:
        log.error(f"❌ Başlangıç hatası: {e}")
        return False

def keep_alive_simple():
    """Basit keep-alive (Flask olmadan)"""
    try:
        # Thread ile basit bir döngü
        import threading
        
        def ping():
            while True:
                time.sleep(300)  # 5 dakika
                log.info("🔄 Keep-alive ping")
        
        thread = threading.Thread(target=ping, daemon=True)
        thread.start()
        log.info("✅ Keep-alive başlatıldı")
        
    except Exception as e:
        log.warning(f"Keep-alive hatası: {e}")

# ==================== ANA PROGRAM ====================
def main():
    """Ana program"""
    log.info("=" * 50)
    log.info("🤖 BURSADAN ESİNTİLER BOT")
    log.info("=" * 50)
    
    # Token kontrolü
    if not TOKEN:
        log.error("❌ TOKEN YOK!")
        return
    
    log.info(f"🔑 Token: ...{TOKEN[-8:]}")
    log.info(f"📢 Kanal: {CHANNEL}")
    
    # Saat bilgisi
    tr_tz = pytz.timezone('Europe/Istanbul')
    tr_time = datetime.now(tr_tz).strftime('%d.%m.%Y %H:%M:%S')
    log.info(f"🕐 Türkiye: {tr_time}")
    log.info(f"🌐 UTC: {datetime.utcnow().strftime('%H:%M:%S')}")
    
    # Başlangıç testi
    success = asyncio.run(startup_test())
    if not success:
        log.warning("⚠️ Başlangıç testi başarısız, devam ediliyor...")
    
    # Zamanlamaları ayarla
    scheduler = setup_schedule()
    
    # Keep-alive başlat
    keep_alive_simple()
    
    log.info("✅ Bot çalışmaya başladı!")
    log.info("=" * 50)
    
    # Hemen gelecek mesajları kontrol et
    now_trt = datetime.now(tr_tz).strftime('%H:%M')
    upcoming = [m for m in MESSAGES if m['time'] > now_trt]
    log.info(f"⏳ Bekleyen mesajlar: {len(upcoming)}")
    
    for msg in upcoming[:3]:  # İlk 3'ü göster
        log.info(f"   → {msg['time']}: {msg['message'][:30]}...")
    
    # Ana döngü
    try:
        while True:
            scheduler.run_pending()
            time.sleep(1)
            
            # Her dakika kontrol
            if datetime.now().second == 0:
                # Her 10 dakikada bir log
                if datetime.now().minute % 10 == 0:
                    log.info(f"📊 Çalışıyor: {datetime.now().strftime('%H:%M')} UTC")
                    
    except KeyboardInterrupt:
        log.info("👋 Bot durduruluyor...")
    except Exception as e:
        log.error(f"💥 Hata: {e}")

if __name__ == '__main__':
    main()
