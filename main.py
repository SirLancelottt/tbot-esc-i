#!/usr/bin/env python3
"""
TELEGRAM BOT - RAILWAY ALWAYS ON FIX
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
import requests  # ⭐ EKLENDİ
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Bot

# ==================== AYARLAR ====================
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHANNEL = os.getenv('TELEGRAM_CHANNEL', '@bursadeneyimlerimiz')

# ==================== LOG ====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)

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
    print("🌐 Health server: 0.0.0.0:8080")
    server.serve_forever()

# ==================== KEEP-ALIVE ====================
def keep_container_alive():
    """Railway container'ı 7/24 uyanık tut"""
    print("🔋 Keep-alive aktif - Container durmayacak")
    while True:
        try:
            # Kendine HTTP isteği at (aktivite)
            requests.get("http://localhost:8080", timeout=10)
            # Her 3.5 dakikada bir (Railway 5 dakikada durduruyor)
            time.sleep(210)  # 3.5 dakika
        except Exception as e:
            # Hata önemsiz, devam et
            time.sleep(60)

# ==================== TOKEN TEST ====================
async def check_token():
    try:
        bot = Bot(token=TOKEN)
        me = await bot.get_me()
        print(f"✅ Bot: @{me.username}")
        return True
    except Exception as e:
        print(f"❌ Token hatası: {e}")
        return False

# ==================== ANA BOT ====================
def run_bot():
    print("\n" + "="*60)
    print("🤖 TELEGRAM BOT - ALWAYS ON FIX")
    print("="*60)
    print(f"🔑 Token: {'✅ VAR' if TOKEN else '❌ YOK'}")
    print(f"📢 Kanal: {CHANNEL}")
    print("="*60)
    
    if not TOKEN:
        print("❌ Token yok!")
        return
    
    # Token test
    if not asyncio.run(check_token()):
        return
    
    # Zamanlamaları ayarla
    try:
        with open("timer.json", "r", encoding="utf-8") as f:
            timer = json.load(f)
        with open("message.json", "r", encoding="utf-8") as f:
            messages = json.load(f)
        
        schedules = timer.get('schedule', [])
        msg_dict = messages.get('messages', {})
        
        print(f"\n⏰ {len(schedules)} zamanlama")
        
        for item in schedules:
            if item.get('disabled'):
                continue
            
            tr_time = item.get('time')
            username = item.get('username')
            
            if not tr_time or not username:
                continue
            
            # UTC'ye çevir
            try:
                tr_tz = pytz.timezone('Europe/Istanbul')
                hour, minute = map(int, tr_time.split(':'))
                today = datetime.now().date()
                
                tr_dt = tr_tz.localize(datetime(today.year, today.month, today.day, hour, minute, 0))
                utc_time = tr_dt.astimezone(pytz.UTC).strftime('%H:%M')
                
                print(f"✓ {tr_time} TRT → {utc_time} UTC - @{username}")
            except:
                pass
                
    except Exception as e:
        print(f"❌ JSON hatası: {e}")
    
    print("\n✅ Bot hazır! Container 7/24 çalışacak...")
    
    # Ana döngü
    minutes = 0
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
            minutes += 1/60
            
            if minutes % 5 == 0:  # Her 5 dakikada
                print(f"⏱️ {int(minutes)} dakikadır kesintisiz çalışıyor")
                
    except KeyboardInterrupt:
        print("\n👋 Durduruldu")
    except Exception as e:
        print(f"\n💥 Hata: {e}")

# ==================== BAŞLAT ====================
if __name__ == '__main__':
    # 1. Keep-alive thread (Container durmasın)
    keep_thread = threading.Thread(target=keep_container_alive, daemon=True)
    keep_thread.start()
    
    # 2. Health server
    health_thread = threading.Thread(target=health_server, daemon=True)
    health_thread.start()
    
    # 3. Ana bot
    run_bot()
