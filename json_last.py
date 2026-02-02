#!/usr/bin/env python3
"""
ZAMANLANMIŞ MESAJ BOT - MESAJI OLDUĞU GİBİ GÖNDER
KULLANICI ADI KESİNLİKLE EKLENMEZ
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
import requests
from datetime import datetime, timedelta
from telegram import Bot

# ==================== AYARLAR ====================
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHANNEL = os.getenv('TELEGRAM_CHANNEL', '@bursadeneyimlerimiz')

# Yerel JSON dosyaları
SCHEDULE_LOCAL = "timer.json"
MESSAGES_LOCAL = "message.json"

# ==================== LOG ====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
log = logging.getLogger()

# ==================== JSON YÜKLEME ====================
def load_all_jsons():
    """JSON'ları yükle"""
    try:
        with open(SCHEDULE_LOCAL, 'r', encoding='utf-8') as f:
            schedule_data = json.load(f)
        with open(MESSAGES_LOCAL, 'r', encoding='utf-8') as f:
            messages_data = json.load(f)
        return schedule_data, messages_data
    except Exception as e:
        log.error(f"❌ JSON okuma hatası: {e}")
        return None, None

# ==================== MESAJ GÖNDERME ====================
async def send_scheduled_message(schedule_item, messages_dict):
    """Zamanlanmış mesajı gönder - KESİNLİKLE USERNAME EKLEMEZ"""
    try:
        if schedule_item.get('disabled', False):
            return False
        
        username = schedule_item.get('username', '')
        
        if not username or username not in messages_dict:
            return False
        
        # RANDOM mesaj seç
        message_pool = messages_dict[username]
        if not message_pool:
            return False
        
        message_data = random.choice(message_pool)
        bot = Bot(token=TOKEN)
        message_text = message_data.get('text', '')
        
        # ⭐ KESİNLİKLE HİÇBİR ŞEY EKLEME - MESAJI OLDUĞU GİBİ GÖNDER
        final_message = message_text  # BU KADAR! Hiçbir şey eklemiyoruz!
        
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
                log.info(f"✅ [📷] @{username}")
            else:
                await bot.send_message(
                    chat_id=CHANNEL,
                    text=final_message,
                    parse_mode='HTML'
                )
                log.warning(f"⚠️ Resim yok: @{username}")
        
        else:  # text_only
            await bot.send_message(
                chat_id=CHANNEL,
                text=final_message,
                parse_mode='HTML'
            )
            log.info(f"✅ [📝] @{username}")
            
        return True
        
    except Exception as e:
        log.error(f"❌ Gönderme hatası: {e}")
        return False

def create_message_sender(schedule_item, messages_dict):
    def sender():
        asyncio.run(send_scheduled_message(schedule_item, messages_dict))
    return sender

# ==================== ZAMANLAMA AYARI ====================
def setup_schedule():
    """Zamanlamaları ayarla"""
    schedule_data, messages_data = load_all_jsons()
    
    if not schedule_data or not messages_data:
        print("❌ JSON'lar yüklenemedi!")
        return schedule, 0
    
    schedule_list = schedule_data.get('schedule', [])
    messages_dict = messages_data.get('messages', {})
    
    # Aktif zamanlama sayısını hesapla (disabled olmayanlar)
    active_schedules = 0
    for item in schedule_list:
        if not item.get('disabled', False):
            active_schedules += 1
    
    # ⭐ ÇOK KISA BAŞLANGIÇ MESAJI
    print("\n🤖 BOT BAŞLADI")
    print(f"⏰ {active_schedules} mesaj bekleniyor\n")
    
    scheduled_count = 0
    for item in schedule_list:
        if item.get('disabled', False):
            continue
        
        tr_time = item.get('time')
        username = item.get('username', '')
        
        if not tr_time or not username or username not in messages_dict:
            continue
        
        # TR → UTC
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
            log.error(f"   Zaman hatası: {e}")
            continue
        
        # Zamanla
        try:
            sender_func = create_message_sender(item, messages_dict)
            schedule.every().day.at(utc_time).do(sender_func)
            
            pool_size = len(messages_dict[username])
            log.info(f"✓ {tr_time} TRT → {utc_time} UTC - @{username}")
            scheduled_count += 1
            
        except Exception as e:
            log.error(f"✗ Zamanlama hatası: {e}")
    
    log.info(f"✅ {scheduled_count} zamanlama ayarlandı")
    return schedule, active_schedules

# ==================== ANA PROGRAM ====================
def main():
    if not TOKEN:
        print("❌ TELEGRAM_TOKEN bulunamadı!")
        return
    
    # Zamanlamaları ayarla
    scheduler, active_count = setup_schedule()
    
    # Ana döngü
    try:
        while True:
            scheduler.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Bot durduruldu")
    except Exception as e:
        log.error(f"💥 Hata: {e}")

if __name__ == '__main__':
    main()