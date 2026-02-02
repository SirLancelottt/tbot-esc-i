#!/usr/bin/env python3
"""
BASIT TELEGRAM BOT - REPLIT UYUMLU
"""

import os
import sys
import time
import logging
import asyncio
from datetime import datetime
import pytz

# Telegram
try:
    from telegram import Bot
    from telegram.error import TelegramError
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    print("❌ python-telegram-bot kurulu değil!")

# ==================== AYARLAR ====================
TOKEN = os.getenv('TELEGRAM_TOKEN', '')
CHANNEL = os.getenv('TELEGRAM_CHANNEL', '@bursadeneyimlerimiz')

# ==================== LOG ====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
log = logging.getLogger()

# ==================== FONKSİYONLAR ====================
def log_start():
    """Başlangıç bilgileri"""
    log.info("=" * 50)
    log.info("🤖 TELEGRAM BOT - BURSADAN ESİNTİLER")
    log.info("=" * 50)
    
    # Token kontrolü
    if not TOKEN:
        log.error("❌ TELEGRAM_TOKEN YOK!")
        log.info("Replit → Tools → Secrets ekleyin")
        return False
    
    if ':' not in TOKEN:
        log.error("❌ Token formatı yanlış! '123456789:ABCdef...' şeklinde olmalı")
        return False
    
    log.info(f"✅ Token: ...{TOKEN[-8:]}")
    log.info(f"📢 Kanal: {CHANNEL}")
    
    # Saat bilgisi
    try:
        tr_tz = pytz.timezone('Europe/Istanbul')
        tr_time = datetime.now(tr_tz).strftime('%d.%m.%Y %H:%M:%S')
        log.info(f"🕐 Türkiye: {tr_time}")
    except:
        pass
    
    return True

async def test_connection():
    """Bağlantı testi"""
    try:
        log.info("🔗 Bağlantı testi...")
        bot = Bot(token=TOKEN)
        
        # Bot bilgisi
        me = await bot.get_me()
        log.info(f"🤖 Bot: @{me.username} ({me.first_name})")
        
        # Kanal kontrolü
        try:
            chat = await bot.get_chat(CHANNEL)
            log.info(f"📢 Kanal: {chat.title}")
            
            # Test mesajı
            await bot.send_message(
                chat_id=CHANNEL,
                text='✅ <b>BOT AKTİF!</b>\nBağlantı testi başarılı.',
                parse_mode='HTML'
            )
            log.info("✅ Test mesajı gönderildi")
            return True
            
        except TelegramError as e:
            log.error(f"❌ Kanal hatası: {e}")
            log.warning("⚠️ Bot admin mi? Kanal doğru mu?")
            return False
            
    except Exception as e:
        log.error(f"❌ Bağlantı hatası: {e}")
        return False

def keep_alive():
    """Replit için keep-alive"""
    try:
        from flask import Flask
        from threading import Thread
        
        app = Flask(__name__)
        
        @app.route('/')
        def home():
            return 'Bot çalışıyor! 🚀'
        
        @app.route('/health')
        def health():
            return {'status': 'ok', 'time': datetime.now().isoformat()}
        
        Thread(target=lambda: app.run(
            host='0.0.0.0', 
            port=8080, 
            debug=False, 
            use_reloader=False
        )).start()
        
        log.info("🌐 Keep-alive server başlatıldı (port 8080)")
        return True
    except Exception as e:
        log.warning(f"Keep-alive başlatılamadı: {e}")
        return False

async def send_daily_messages():
    """Günlük mesajları gönder"""
    try:
        bot = Bot(token=TOKEN)
        
        # Mesaj listesi
        messages = [
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
            {'time': '24:00', 'message': '🌙 <b>İYİ GECELER</b>\n\nYarın daha güzel bir gün olacak! ✨'}
        ]
        
        log.info(f"📅 {len(messages)} mesaj zamanlandı")
        
        # Şimdilik sadece log
        for time_str, msg in messages:
            log.info(f"   ⏰ {time_str}: {msg[:30]}...")
        
        return True
    except Exception as e:
        log.error(f"Mesaj ayarlama hatası: {e}")
        return False

async def main_async():
    """Ana async fonksiyon"""
    # Başlangıç
    if not log_start():
        return
    
    # Bağlantı testi
    if not await test_connection():
        log.warning("⚠️ Bağlantı hatası, ama devam ediliyor...")
    
    # Keep-alive
    keep_alive()
    
    # Mesajları ayarla
    await send_daily_messages()
    
    log.info("✅ Bot başlatıldı!")
    log.info("=" * 50)
    
    # Sonsuz döngü
    try:
        while True:
            # Her 30 saniyede bir durum
            await asyncio.sleep(30)
            log.info("📡 Bot aktif...")
            
    except KeyboardInterrupt:
        log.info("👋 Bot durduruluyor...")
    except Exception as e:
        log.error(f"💥 Beklenmeyen hata: {e}")

def main():
    """Ana giriş noktası"""
    try:
        # Async çalıştır
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\n👋 Bot durduruldu")
    except Exception as e:
        print(f"💥 CRITICAL HATA: {e}")
        import traceback
        traceback.print_exc()

# ==================== BAŞLANGIÇ ====================
if __name__ == '__main__':
    main()
    print("Program sonlandı.")