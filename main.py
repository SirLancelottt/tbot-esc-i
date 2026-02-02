#!/usr/bin/env python3
"""
TELEGRAM ZAMANLANMIŞ MESAJ BOT - RAILWAY FIXED
CONTAINER DURMAYACAK ŞEKİLDE
"""

import os
import sys
import time
import json
import random
import schedule
import logging
import asyncio
import pytz
from datetime import datetime
from telegram import Bot, error

# ==================== AYARLAR ====================
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHANNEL = os.getenv('TELEGRAM_CHANNEL', '@bursadeneyimlerimiz')

# JSON dosyaları
SCHEDULE_LOCAL = "timer.json"
MESSAGES_LOCAL = "message.json"

# ==================== LOG ====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)  # Railway log için
    ]
)
log = logging.getLogger(__name__)

# ==================== BAŞLANGIÇ ====================
print("\n" + "="*60)
print("🤖 TELEGRAM BOT - RAILWAY FIXED VERSION")
print("="*60)
print(f"📱 Token: {'✅ VAR' if TOKEN else '❌ YOK'}")
print(f"📢 Kanal: {CHANNEL}")
print("="*60)

if not TOKEN:
    log.error("❌ TELEGRAM_TOKEN bulunamadı! Railway Variables kontrol edin.")
    sys.exit(1)

# ==================== JSON YÜKLEME ====================
def load_all_jsons():
    try:
        with open(SCHEDULE_LOCAL, 'r', encoding='utf-8') as f:
            schedule_data = json.load(f)
        with open(MESSAGES_LOCAL, 'r', encoding='utf-8') as f:
            messages_data = json.load(f)
        return schedule_data, messages_data
    except Exception as e:
        log.error(f"JSON okuma hatası: {e}")
        return None, None

# ==================== MESAJ GÖNDERME ====================
async def send_scheduled_message(schedule_item, messages_dict):
    try:
        if schedule_item.get('disabled', False):
            return False
        
        username = schedule_item.get('username', '')
        
        if not username or username not in messages_dict:
            return False
        
        message_pool = messages_dict[username]
        if not message_pool:
            return False
        
        message_data = random.choice(message_pool)
        bot = Bot(token=TOKEN)
        message_text = message_data.get('text', '')
        
        # MESAJI OLDUĞU GİBİ GÖNDER
        final_message = message_text
        
        log.info(f"📤 @{username} gönderiliyor...")
        
        msg_type = message_data.get('type', 'text_only')
        
        if msg_type == 'with_image':
            image_url = message_data.get('image_url')
            
            if image_url:
                await bot.send_photo(
                    chat_id=CHANNEL,
                    photo=image_url,
                    caption=final_message,
                    parse_mode='HTML'
                )
                log.info(f"✅ @{username} - Resimli gönderildi")
            else:
                await bot.send_message(
                    chat_id=CHANNEL,
                    text=final_message,
                    parse_mode='HTML'
                )
                log.info(f"✅ @{username} - Metin gönderildi")
        
        else:
            await bot.send_message(
                chat_id=CHANNEL,
                text=final_message,
                parse_mode='HTML'
            )
            log.info(f"✅ @{username} - Metin gönderildi")
            
        return True
        
    except error.Unauthorized:
        log.error("❌ Token geçersiz! Yeni token alın.")
        return False
    except Exception as e:
        log.error(f"❌ Gönderme hatası: {e}")
        return False

def create_message_sender(schedule_item, messages_dict):
    def sender():
        asyncio.run(send_scheduled_message(schedule_item, messages_dict))
    return sender

# ==================== ZAMANLAMA AYARI ====================
def setup_schedule():
    log.info("🚀 Zamanlamalar ayarlanıyor...")
    
    schedule_data, messages_data = load_all_jsons()
    
    if not schedule_data or not messages_data:
        log.error("❌ JSON'lar yüklenemedi!")
        return None, 0
    
    schedule_list = schedule_data.get('schedule', [])
    messages_dict = messages_data.get('messages', {})
    
    active_schedules = 0
    for item in schedule_list:
        if not item.get('disabled', False):
            active_schedules += 1
    
    log.info(f"📊 {active_schedules} aktif zamanlama")
    log.info(f"💬 {len(messages_dict)} kullanıcı")
    
    scheduled_count = 0
    for item in schedule_list:
        if item.get('disabled', False):
            continue
        
        tr_time = item.get('time')
        username = item.get('username', '')
        
        if not tr_time or not username or username not in messages_dict:
            continue
        
        try:
            tr_tz = pytz.timezone('Europe/Istanbul')
            hour, minute = map(int, tr_time.split(':'))
            today = datetime.now().date()
            
            tr_datetime = tr_tz.localize(
                datetime(today.year, today.month, today.day, hour, minute, 0)
            )
            utc_datetime = tr_datetime.astimezone(pytz.UTC)
            utc_time = utc_datetime.strftime('%H:%M')
            
        except Exception as e:
            log.error(f"⏰ Zaman hatası: {e}")
            continue
        
        try:
            sender_func = create_message_sender(item, messages_dict)
            schedule.every().day.at(utc_time).do(sender_func)
            log.info(f"✓ {tr_time} TRT → {utc_time} UTC - @{username}")
            scheduled_count += 1
            
        except Exception as e:
            log.error(f"✗ Zamanlama hatası: {e}")
    
    log.info(f"✅ {scheduled_count} zamanlama ayarlandı")
    return schedule, active_schedules

# ==================== ANA PROGRAM ====================
def main():
    log.info("="*50)
    log.info("🤖 BOT ÇALIŞMAYA BAŞLADI")
    log.info("="*50)
    
    scheduler, active_count = setup_schedule()
    
    if not scheduler:
        log.error("❌ Zamanlama ayarlanamadı!")
        return
    
    log.info(f"⏰ {active_count} mesaj bekleniyor...")
    
    # ⭐⭐ RAILWAY İÇİN KRİTİK: SÜREKLİ ACTIVITY ⭐⭐
    activity_counter = 0
    last_log_time = time.time()
    
    try:
        while True:
            # 1. Schedule'ı çalıştır
            schedule.run_pending()
            
            # 2. Railway için activity yarat
            activity_counter += 1
            
            # ⭐ HER 10 SANİYEDE BİR EKRANA YAZ (CONTAINER DURMASIN)
            current_time = time.time()
            if current_time - last_log_time >= 10:  # 10 saniyede bir
                # Ekrana aktivite göster
                print("💓", end="", flush=True)
                
                # Her 6 aktivitede bir log (1 dakika)
                if activity_counter % 6 == 0:
                    minutes_running = (activity_counter * 10) // 60
                    log.info(f"⏱️ {minutes_running} dakikadır çalışıyor...")
                
                last_log_time = current_time
            
            # 3. Kısa bekle
            time.sleep(1)
            
    except KeyboardInterrupt:
        log.info("\n👋 Bot durduruldu")
    except Exception as e:
        log.error(f"💥 Beklenmeyen hata: {e}")

if __name__ == '__main__':
    main()
