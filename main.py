#!/usr/bin/env python3
"""
TELEGRAM ZAMANLANMIŞ MESAJ BOT - RAILWAY FINAL FIXED ASYNC
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
import threading
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Bot
from telegram.error import Unauthorized  # ⭐ DÜZELTME

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
    handlers=[logging.StreamHandler(sys.stdout)]
)
log = logging.getLogger(__name__)

# ==================== HTTP HEALTH SERVER ====================
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Bot aktif!')
    
    def log_message(self, format, *args):
        pass

def run_health_server():
    server = HTTPServer(('0.0.0.0', 8080), HealthHandler)
    print("🌐 Health server başladı: 0.0.0.0:8080")
    server.serve_forever()

# ==================== BOT BAŞLANGIÇ MESAJI ====================
async def send_startup_message():
    try:
        bot = Bot(token=TOKEN)
        startup_msg = (
            "🤖 *BOT BAŞLATILDI*\n\n"
            "✅ Zamanlanmış mesaj sistemi aktif\n"
            "⏰ Otomatik gönderim başladı\n"
            "📊 Sistem: Railway Docker\n\n"
            "_Her şey yolunda!_ ✨"
        )
        
        await bot.send_message(
            chat_id=CHANNEL,
            text=startup_msg,
            parse_mode='Markdown'
        )
        log.info("✅ Başlangıç mesajı gönderildi")
        return True
    except Exception as e:
        log.error(f"❌ Başlangıç mesajı hatası: {e}")
        return False

# ==================== TOKEN TEST ====================
async def test_token():
    """Token'in geçerli olup olmadığını test et"""
    try:
        bot = Bot(token=TOKEN)
        bot_info = await bot.get_me()  # ⭐ AWAIT EKLENDİ
        log.info(f"✅ Token geçerli! Bot: @{bot_info.username}")
        return True
    except Unauthorized:
        log.error("❌ Token geçersiz! Yeni token alın ve Railway'da güncelleyin.")
        return False
    except Exception as e:
        log.error(f"❌ Token test hatası: {e}")
        return False

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
                log.info(f"✅ @{username} - Resimli")
            else:
                await bot.send_message(
                    chat_id=CHANNEL,
                    text=final_message,
                    parse_mode='HTML'
                )
                log.info(f"✅ @{username} - Metin")
        
        else:
            await bot.send_message(
                chat_id=CHANNEL,
                text=final_message,
                parse_mode='HTML'
            )
            log.info(f"✅ @{username} - Metin")
            
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
    print("\n" + "="*60)
    print("🤖 TELEGRAM BOT - RAILWAY FINAL FIXED ASYNC")
    print("="*60)
    print(f"📱 Token: {'✅ VAR' if TOKEN else '❌ YOK'}")
    if TOKEN:
        print(f"📱 Token İlk 10: {TOKEN[:10]}...")
    print(f"📢 Kanal: {CHANNEL}")
    print("="*60)
    
    if not TOKEN:
        log.error("❌ TELEGRAM_TOKEN bulunamadı!")
        sys.exit(1)
    
    # TOKEN TEST (ASYNC)
    log.info("🔍 Token test ediliyor...")
    token_valid = asyncio.run(test_token())  # ⭐ ASYNC ÇAĞIR
    if not token_valid:
        return
    
    # BAŞLANGIÇ MESAJI
    log.info("📨 Başlangıç mesajı gönderiliyor...")
    try:
        asyncio.run(send_startup_message())
    except Exception as e:
        log.warning(f"⚠️ Başlangıç mesajı gönderilemedi: {e}")
    
    # ZAMANLAMALARI AYARLA
    scheduler, active_schedules = setup_schedule()
    
    if not scheduler:
        log.error("❌ Zamanlama ayarlanamadı!")
        return
    
    log.info(f"⏰ {active_schedules} mesaj bekleniyor...")
    log.info("✅ Bot tamamen hazır!")
    
    # ANA DÖNGÜ
    activity_counter = 0
    try:
        while True:
            schedule.run_pending()
            
            activity_counter += 1
            
            # Her 30 saniyede bir nokta
            if activity_counter % 30 == 0:
                print(".", end="", flush=True)
            
            # Her 5 dakikada log
            if activity_counter % 300 == 0:
                minutes = activity_counter // 60
                log.info(f"⏱️ {minutes} dakikadır kesintisiz çalışıyor")
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        log.info("\n👋 Bot durduruldu")
    except Exception as e:
        log.error(f"💥 Beklenmeyen hata: {e}")

# ==================== PROGRAM BAŞLATMA ====================
if __name__ == '__main__':
    # HTTP Server başlat
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()
    
    # Ana bot
    main()
