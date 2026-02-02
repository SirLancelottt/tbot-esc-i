#!/usr/bin/env python3
"""
TELEGRAM BOT - RAILWAY ULTIMATE FIX
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
from telegram.error import Unauthorized

# ==================== AYARLAR ====================
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHANNEL = os.getenv('TELEGRAM_CHANNEL', '@bursadeneyimlerimiz')

# ==================== LOG ====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)

print("\n" + "="*60)
print("🚀 TELEGRAM BOT - ULTIMATE FIX VERSION")
print("="*60)
print(f"Token: {'✅' if TOKEN else '❌'}")
print(f"Kanal: {CHANNEL}")
print("="*60)

# ==================== HTTP SERVER ====================
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'OK')
    def log_message(self, *args):
        pass

def health_server():
    server = HTTPServer(('0.0.0.0', 8080), HealthHandler)
    print("🌐 Health: 0.0.0.0:8080")
    server.serve_forever()

# ==================== TOKEN TEST ====================
async def check_token():
    try:
        bot = Bot(token=TOKEN)
        me = await bot.get_me()
        print(f"✅ Bot: @{me.username}")
        return True
    except Unauthorized:
        print("❌ Token geçersiz!")
        return False
    except Exception as e:
        print(f"❌ Hata: {e}")
        return False

# ==================== BAŞLANGIÇ MESAJI ====================
async def send_welcome():
    try:
        bot = Bot(token=TOKEN)
        msg = "🤖 *BOT AKTİF*\n\nZamanlanmış mesaj sistemi çalışıyor! ✅"
        await bot.send_message(CHANNEL, msg, parse_mode='Markdown')
        print("📨 Başlangıç mesajı gönderildi")
    except Exception as e:
        print(f"⚠️ Başlangıç mesajı hatası: {e}")

# ==================== MESAJ GÖNDERME ====================
def load_jsons():
    try:
        with open("timer.json", "r", encoding="utf-8") as f:
            timer = json.load(f)
        with open("message.json", "r", encoding="utf-8") as f:
            messages = json.load(f)
        return timer, messages
    except Exception as e:
        print(f"❌ JSON hatası: {e}")
        return None, None

async def send_message(username, text):
    try:
        bot = Bot(token=TOKEN)
        await bot.send_message(CHANNEL, text, parse_mode='HTML')
        print(f"✅ @{username} gönderildi")
    except Exception as e:
        print(f"❌ Gönderme hatası: {e}")

def create_sender(username, text):
    def sender():
        asyncio.run(send_message(username, text))
    return sender

# ==================== ANA PROGRAM ====================
def main():
    if not TOKEN:
        print("❌ Token yok!")
        return
    
    # Token test
    if not asyncio.run(check_token()):
        return
    
    # Başlangıç mesajı
    asyncio.run(send_welcome())
    
    # JSON yükle
    timer_data, msg_data = load_jsons()
    if not timer_data or not msg_data:
        return
    
    schedules = timer_data.get('schedule', [])
    messages = msg_data.get('messages', {})
    
    print(f"\n⏰ {len(schedules)} zamanlama")
    print(f"💬 {len(messages)} kullanıcı")
    
    # Zamanlamaları ayarla
    for item in schedules:
        if item.get('disabled'):
            continue
        
        time_str = item.get('time')
        username = item.get('username')
        
        if not time_str or not username or username not in messages:
            continue
        
        # UTC'ye çevir
        try:
            tr_tz = pytz.timezone('Europe/Istanbul')
            hour, minute = map(int, time_str.split(':'))
            today = datetime.now().date()
            
            tr_time = tr_tz.localize(datetime(today.year, today.month, today.day, hour, minute, 0))
            utc_time = tr_time.astimezone(pytz.UTC).strftime('%H:%M')
            
            # Rastgele mesaj seç
            pool = messages[username]
            if pool:
                msg = random.choice(pool).get('text', '')
                schedule.every().day.at(utc_time).do(create_sender(username, msg))
                print(f"✓ {time_str} → {utc_time} UTC - @{username}")
        except Exception as e:
            print(f"✗ Zamanlama hatası: {e}")
    
    print("\n✅ Bot hazır! Bekleniyor...\n")
    
    # Ana döngü
    counter = 0
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
            counter += 1
            
            if counter % 30 == 0:
                print(".", end="", flush=True)
            
            if counter % 300 == 0:
                print(f"\n⏱️ {counter//60} dakika çalıştı")
                
    except KeyboardInterrupt:
        print("\n👋 Durduruldu")
    except Exception as e:
        print(f"\n💥 Hata: {e}")

# ==================== BAŞLAT ====================
if __name__ == '__main__':
    # Health server
    thread = threading.Thread(target=health_server, daemon=True)
    thread.start()
    
    # Ana bot
    main()
