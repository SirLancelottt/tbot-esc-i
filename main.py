#!/usr/bin/env python3
"""
TELEGRAM BOT - RAILWAY ULTIMATE FIX
FINAL VERSION
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
from telegram.error import BadRequest, Forbidden  # ⭐ DÜZELTİLDİ

# ==================== AYARLAR ====================
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHANNEL = os.getenv('TELEGRAM_CHANNEL', '@bursadeneyimlerimiz')

# JSON dosyaları
TIMER_FILE = "timer.json"
MESSAGE_FILE = "message.json"

# ==================== LOG ====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)

# BAŞLANGIÇ
print("\n" + "="*60)
print("🤖 TELEGRAM BOT - FINAL WORKING VERSION")
print("="*60)

# ==================== HTTP SERVER ====================
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Bot aktif!')
    
    def log_message(self, format, *args):
        pass  # Log'u gizle

def run_health_server():
    server = HTTPServer(('0.0.0.0', 8080), HealthHandler)
    print("🌐 Health server: 0.0.0.0:8080")
    server.serve_forever()

# ==================== BOT FONKSİYONLARI ====================
async def test_bot_token():
    """Token'in geçerli olup olmadığını kontrol et"""
    try:
        bot = Bot(token=TOKEN)
        me = await bot.get_me()
        print(f"✅ Token geçerli! Bot: @{me.username}")
        print(f"   Bot ID: {me.id}")
        print(f"   Bot Adı: {me.first_name}")
        return True
    except Exception as e:
        print(f"❌ Token hatası: {e}")
        return False

async def send_start_message():
    """Bot başladığında kanala mesaj gönder"""
    try:
        bot = Bot(token=TOKEN)
        message = (
            "🤖 *BOT SİSTEMİ AKTİF* 🚀\n\n"
            "✅ Zamanlanmış mesaj botu çalışmaya başladı\n"
            "⏰ Otomatik gönderim aktif\n"
            "📊 Railway Docker üzerinde çalışıyor\n\n"
            "_Sorunsuz şekilde çalışıyor..._ ✨"
        )
        await bot.send_message(
            chat_id=CHANNEL,
            text=message,
            parse_mode='Markdown'
        )
        print("📨 Başlangıç mesajı gönderildi")
        return True
    except Exception as e:
        print(f"⚠️ Başlangıç mesajı hatası: {e}")
        return False

# ==================== JSON İŞLEMLERİ ====================
def load_json_files():
    """JSON dosyalarını yükle"""
    try:
        with open(TIMER_FILE, 'r', encoding='utf-8') as f:
            timer_data = json.load(f)
        with open(MESSAGE_FILE, 'r', encoding='utf-8') as f:
            message_data = json.load(f)
        return timer_data, message_data
    except Exception as e:
        print(f"❌ JSON yükleme hatası: {e}")
        return None, None

# ==================== MESAJ GÖNDERME ====================
async def send_scheduled_post(username, message_text):
    """Zamanlanmış mesajı gönder"""
    try:
        bot = Bot(token=TOKEN)
        await bot.send_message(
            chat_id=CHANNEL,
            text=message_text,
            parse_mode='HTML'
        )
        print(f"✅ @{username} gönderildi")
        return True
    except Exception as e:
        print(f"❌ Gönderme hatası @{username}: {e}")
        return False

def create_message_job(username, message_text):
    """Schedule için iş oluştur"""
    def job():
        asyncio.run(send_scheduled_post(username, message_text))
    return job

# ==================== ZAMANLAMA ====================
def setup_schedules():
    """Zamanlamaları ayarla"""
    print("⏰ Zamanlamalar ayarlanıyor...")
    
    timer_data, message_data = load_json_files()
    if not timer_data or not message_data:
        return None, 0
    
    schedule_list = timer_data.get('schedule', [])
    messages_dict = message_data.get('messages', {})
    
    active_count = 0
    for item in schedule_list:
        if not item.get('disabled', False):
            active_count += 1
    
    print(f"   📊 Aktif zamanlama: {active_count}")
    print(f"   👤 Kullanıcı sayısı: {len(messages_dict)}")
    
    # Her kullanıcı için mesaj sayısı
    for user, pool in messages_dict.items():
        print(f"      @{user}: {len(pool)} mesaj")
    
    scheduled_jobs = 0
    
    for item in schedule_list:
        if item.get('disabled', False):
            continue
        
        tr_time = item.get('time', '')
        username = item.get('username', '')
        
        if not tr_time or not username or username not in messages_dict:
            continue
        
        # Zamanı UTC'ye çevir
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
            print(f"   ⚠️ Zaman hatası {tr_time}: {e}")
            continue
        
        # Mesaj havuzundan rastgele seç
        message_pool = messages_dict[username]
        if not message_pool:
            continue
        
        selected_message = random.choice(message_pool)
        message_text = selected_message.get('text', '')
        
        if not message_text:
            continue
        
        # Zamanlamayı ayarla
        try:
            job_func = create_message_job(username, message_text)
            schedule.every().day.at(utc_time).do(job_func)
            print(f"   ✓ {tr_time} TRT → {utc_time} UTC - @{username}")
            scheduled_jobs += 1
        except Exception as e:
            print(f"   ✗ Zamanlama hatası: {e}")
    
    print(f"✅ {scheduled_jobs} zamanlama ayarlandı")
    return schedule, active_count

# ==================== ANA PROGRAM ====================
def main():
    print("="*60)
    print(f"🔑 Token: {'✅ VAR' if TOKEN else '❌ YOK'}")
    if TOKEN:
        print(f"   İlk 10 karakter: {TOKEN[:10]}...")
    print(f"📢 Kanal: {CHANNEL}")
    print("="*60)
    
    if not TOKEN:
        print("❌ TELEGRAM_TOKEN bulunamadı!")
        print("   Railway → Variables → TELEGRAM_TOKEN ekleyin")
        return
    
    # 1. Token test
    print("\n🔍 Token test ediliyor...")
    token_ok = asyncio.run(test_bot_token())
    if not token_ok:
        print("❌ Token geçersiz! @BotFather'dan yeni token alın.")
        print("   Railway Variables'da güncelleyin.")
        return
    
    # 2. Başlangıç mesajı
    print("\n📨 Başlangıç mesajı gönderiliyor...")
    asyncio.run(send_start_message())
    
    # 3. Zamanlamaları ayarla
    scheduler, schedule_count = setup_schedules()
    if not scheduler:
        print("❌ Zamanlama ayarlanamadı!")
        return
    
    print(f"\n🎯 {schedule_count} zamanlanmış mesaj bekleniyor...")
    print("💡 Bot Railway'da 7/24 çalışacak")
    print("="*60 + "\n")
    
    # 4. Ana döngü
    minutes_running = 0
    last_minute_check = time.time()
    
    try:
        while True:
            # Schedule'ı çalıştır
            scheduler.run_pending()
            
            # Her dakika kontrol et
            current_time = time.time()
            if current_time - last_minute_check >= 60:  # 1 dakika
                minutes_running += 1
                last_minute_check = current_time
                
                # Her 5 dakikada bir aktivite göster
                if minutes_running % 5 == 0:
                    print(f"⏱️ {minutes_running} dakikadır çalışıyor...")
            
            # Kısa bekle
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n👋 Bot durduruldu")
    except Exception as e:
        print(f"\n💥 Beklenmeyen hata: {e}")

# ==================== PROGRAM BAŞLANGICI ====================
if __name__ == '__main__':
    # Health server'ı başlat (Railway container durmasın)
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()
    
    # Ana programı çalıştır
    main()
