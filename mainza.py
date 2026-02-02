#!/usr/bin/env python3
"""
ÇALIŞAN TELEGRAM BOT - PARAMETRE HATASI DÜZELTİLMİŞ
"""

import os
import sys
import time
import schedule
import logging
import asyncio
import pytz
from datetime import datetime, timedelta
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

# ==================== DÜZELTİLMİŞ MESAJ LİSTESİ ====================
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
    {'time': '20:05', 'message': '🌆 <b>AKŞAM VAKTİ</b>\n\nGünün yorgunluğunu atma zamanı! 🏡'},
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

def create_message_sender(text):
    """Mesaj gönderici fonksiyon oluştur (lambda problemi için)"""
    def sender():
        asyncio.run(send_message_async(text))
    return sender

def fix_time_format(tr_time):
    """24:00 gibi saatleri düzelt"""
    if tr_time == '24:00':
        return '23:59'
    return tr_time

def tr_to_utc(tr_time):
    """TR saati → UTC"""
    try:
        tr_time = fix_time_format(tr_time)
        tr_tz = pytz.timezone('Europe/Istanbul')
        
        hour, minute = map(int, tr_time.split(':'))
        today = datetime.now().date()
        
        tr_datetime = tr_tz.localize(
            datetime(today.year, today.month, today.day, hour, minute, 0)
        )
        
        utc_datetime = tr_datetime.astimezone(pytz.UTC)
        return utc_datetime.strftime('%H:%M')
        
    except Exception as e:
        log.error(f"Zaman çevirme hatası ({tr_time}): {e}")
        default_time = (datetime.utcnow() + timedelta(minutes=1)).strftime('%H:%M')
        return default_time

def setup_schedule():
    """Zamanlamaları ayarla"""
    log.info("⏰ Zamanlamalar ayarlanıyor...")
    
    scheduled_count = 0
    for item in MESSAGES:
        tr_time = item['time']
        message = item['message']
        
        fixed_time = fix_time_format(tr_time)
        if fixed_time != tr_time:
            log.warning(f"   {tr_time} → {fixed_time} (düzeltildi)")
        
        utc_time = tr_to_utc(fixed_time)
        
        try:
            # DOĞRU KULLANIM: Lambda yerine fonksiyon fabrikası
            sender_func = create_message_sender(message)
            schedule.every().day.at(utc_time).do(sender_func)
            
            log.info(f"   ✓ {fixed_time} TRT → {utc_time} UTC")
            scheduled_count += 1
            
        except Exception as e:
            log.error(f"   ✗ {fixed_time} TRT → HATA: {e}")
    
    log.info(f"✅ {scheduled_count}/{len(MESSAGES)} mesaj zamanlandı")
    return schedule

async def startup_test():
    """Başlangıç testi"""
    try:
        bot = Bot(token=TOKEN)
        
        me = await bot.get_me()
        log.info(f"🤖 Bot: @{me.username}")
        
        chat = await bot.get_chat(CHANNEL)
        log.info(f"📢 Kanal: {chat.title}")
        
        # ACİL: Hemen bir test mesajı gönder
        await bot.send_message(
            chat_id=CHANNEL,
            text='🔧 <b>BOT GÜNCELLENDİ</b>\n\n' +
                 f'🕐 {datetime.now().strftime("%H:%M:%S")}\n' +
                 '✅ Parametre hatası düzeltildi!',
            parse_mode='HTML'
        )
        log.info("✅ Test mesajı gönderildi")
        return True
        
    except Exception as e:
        log.error(f"❌ Başlangıç hatası: {e}")
        return False

def keep_alive():
    """Basit keep-alive"""
    try:
        import threading
        
        def ping():
            while True:
                time.sleep(300)
                log.debug("🔄 Ping")
        
        threading.Thread(target=ping, daemon=True).start()
        log.info("✅ Keep-alive başlatıldı")
        
    except Exception as e:
        log.warning(f"Keep-alive hatası: {e}")

# ==================== ANA PROGRAM ====================
def main():
    """Ana program"""
    log.info("=" * 50)
    log.info("🤖 BURSADAN ESİNTİLER BOT - DÜZELTİLMİŞ")
    log.info("=" * 50)
    
    if not TOKEN:
        log.error("❌ TOKEN YOK!")
        return
    
    log.info(f"🔑 Token: ...{TOKEN[-8:]}")
    log.info(f"📢 Kanal: {CHANNEL}")
    
    tr_tz = pytz.timezone('Europe/Istanbul')
    tr_time = datetime.now(tr_tz).strftime('%d.%m.%Y %H:%M:%S')
    log.info(f"🕐 Türkiye: {tr_time}")
    log.info(f"🌐 UTC: {datetime.utcnow().strftime('%H:%M:%S')}")
    
    # ACİL: Hemen mesaj gönder (geç kalmış mesaj için)
    async def send_missed():
        bot = Bot(token=TOKEN)
        await bot.send_message(
            chat_id=CHANNEL,
            text='⏰ <b>KAÇIRILAN MESAJ</b>\n\nGerçek Bayanlar Nerde?',
            parse_mode='HTML'
        )
    
    try:
        asyncio.run(send_missed())
        log.info("✅ Kaçırılan mesaj gönderildi")
    except Exception as e:
        log.error(f"Kaçırılan mesaj hatası: {e}")
    
    # Başlangıç testi
    success = asyncio.run(startup_test())
    if not success:
        log.warning("⚠️ Başlangıç testi başarısız, devam ediliyor...")
    
    # Zamanlamaları ayarla
    scheduler = setup_schedule()
    
    # Keep-alive başlat
    keep_alive()
    
    log.info("✅ Bot çalışmaya başladı!")
    log.info("=" * 50)
    
    # Kalan mesajlar
    now_trt = datetime.now(tr_tz)
    upcoming = []
    for msg in MESSAGES:
        msg_time = fix_time_format(msg['time'])
        msg_hour, msg_minute = map(int, msg_time.split(':'))
        
        if (msg_hour > now_trt.hour) or (msg_hour == now_trt.hour and msg_minute > now_trt.minute):
            upcoming.append(msg)
    
    log.info(f"⏳ Kalan mesajlar: {len(upcoming)}")
    
    # Sonraki 3 mesajı göster
    for i, msg in enumerate(upcoming[:3], 1):
        remaining = (msg_hour - now_trt.hour) * 60 + (msg_hour - now_trt.minute)
        log.info(f"   {i}. {msg['time']} ({remaining} dakika): {msg['message'][:30]}...")
    
    # Ana döngü
    try:
        while True:
            scheduler.run_pending()
            time.sleep(1)
            
            # Her dakika kontrol
            if datetime.now().second == 0:
                # Her 5 dakikada bir log
                if datetime.now().minute % 5 == 0:
                    current = datetime.now(tr_tz).strftime('%H:%M:%S')
                    log.info(f"📡 Çalışıyor... ({current} TRT)")
                    
    except KeyboardInterrupt:
        log.info("👋 Bot durduruluyor...")
    except Exception as e:
        log.error(f"💥 Hata: {e}")

if __name__ == '__main__':
    main()