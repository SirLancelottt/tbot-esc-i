import os
import logging
import schedule
import time
import pytz
from datetime import datetime
from telegram import Bot
from telegram.error import TelegramError

# ==================== KONFİGÜRASYON ====================
# Replit Secrets'tan alınacak değişkenler
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHANNEL = os.getenv('TELEGRAM_CHANNEL', '@bursadeneyimlerimiz')  # Varsayılan kanal

# Zamanlamalar (Türkiye saati - TRT)
MESSAGE_SCHEDULES = [
    {'time': '09:00', 'message': '⏰ <b>GÜNAYDIN!</b>\n\nBugün harika bir gün olacak! ☀️'},
    {'time': '12:00', 'message': '☀️ <b>ÖĞLE VAKTİ</b>\n\nAra verip kendinize iyi bakın! 🍽️'},
    {'time': '14:10', 'message': 'Gerçek Bayanlar Nerde?'},
    {'time': '14:20', 'message': 'Kedicik Kimdir?'},
    {'time': '14:30', 'message': 'Simge Kimdir?'},
    {'time': '15:00', 'message': 'Çağla Kimdir?'},
    {'time': '15:15', 'message': 'Gerçek Bayanlar Nerde?'},
    {'time': '15:30', 'message': 'Kedicik Kimdir?'},
    {'time': '15:45', 'message': 'Simge Kimdir?'},
    {'time': '16:00', 'message': 'Çağla Kimdir?'},
    {'time': '16:15', 'message': 'Gerçek Bayanlar Nerde?'},
    {'time': '16:30', 'message': 'Kedicik Kimdir?'},
    {'time': '16:45', 'message': 'Simge Kimdir?'},
    {'time': '17:00', 'message': 'Çağla Kimdir?'},
    {'time': '20:00', 'message': '🌆 <b>AKŞAM VAKTİ</b>\n\nGünün yorgunluğunu atma zamanı! 🏡'},
    {'time': '24:00', 'message': '🌙 <b>İYİ GECELER</b>\n\nYarın daha güzel bir gün olacak! ✨'}
]

# ==================== LOG AYARLARI ====================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# ==================== BOT FONKSİYONLARI ====================
def send_scheduled_message(message_text):
    """Zamanlanmış mesajı gönder"""
    try:
        bot = Bot(token=TOKEN)
        bot.send_message(
            chat_id=CHANNEL,
            text=message_text,
            parse_mode='HTML',
            disable_web_page_preview=True
        )
        logger.info(f"Mesaj gönderildi: {message_text[:50]}...")
    except Exception as e:
        logger.error(f"Mesaj gönderilemedi: {e}")

def convert_tr_to_utc(tr_time):
    """Türkiye saatini UTC'ye çevir"""
    try:
        tr_tz = pytz.timezone('Europe/Istanbul')
        today = datetime.now().date()
        
        # TR saati ile datetime oluştur
        tr_datetime = tr_tz.localize(
            datetime.combine(today, datetime.strptime(tr_time, '%H:%M').time())
        )
        
        # UTC'ye çevir
        utc_datetime = tr_datetime.astimezone(pytz.UTC)
        utc_time_str = utc_datetime.strftime('%H:%M')
        
        logger.info(f"Zaman çevrildi: {tr_time} TR -> {utc_time_str} UTC")
        return utc_time_str
    except Exception as e:
        logger.error(f"Zaman çevirme hatası: {e}")
        return tr_time

def setup_schedules():
    """Zamanlamaları ayarla"""
    logger.info("Zamanlamalar ayarlanıyor...")
    
    for schedule_item in MESSAGE_SCHEDULES:
        tr_time = schedule_item['time']
        message = schedule_item['message']
        utc_time = convert_tr_to_utc(tr_time)
        
        # Schedule kütüphanesi için zamanı ayarla
        schedule.every().day.at(utc_time).do(
            send_scheduled_message, 
            message_text=message
        )
        
        logger.info(f"{tr_time} TR -> {utc_time} UTC : {message[:30]}...")
    
    logger.info(f"Toplam {len(MESSAGE_SCHEDULES)} zamanlama ayarlandı")
    return schedule

def check_bot_permissions():
    """Bot izinlerini kontrol et"""
    try:
        bot = Bot(token=TOKEN)
        
        # Bot bilgilerini al
        bot_info = bot.get_me()
        logger.info(f"🤖 Bot: @{bot_info.username} ({bot_info.first_name})")
        
        # Kanalı kontrol et
        try:
            chat = bot.get_chat(CHANNEL)
            logger.info(f"📢 Kanal: {chat.title}")
            
            # Test mesajı gönder
            bot.send_message(
                chat_id=CHANNEL,
                text="✅ <b>Bot başlatıldı!</b>\n\nZamanlanmış mesajlar aktif edildi.",
                parse_mode='HTML'
            )
            logger.info("✅ Test mesajı gönderildi")
            return True
            
        except TelegramError as e:
            logger.error(f"❌ Kanal hatası: {e}")
            logger.warning("⚠️ Botu kanala admin olarak eklediğinizden emin olun!")
            return False
            
    except Exception as e:
        logger.error(f"❌ Bot bağlantı hatası: {e}")
        return False

def keep_alive():
    """Botun sürekli çalışmasını sağla (Replit için)"""
    try:
        # UptimeRobot veya benzeri ping servisleri için basit bir endpoint
        from flask import Flask
        app = Flask(__name__)
        
        @app.route('/')
        def home():
            return 'Bot çalışıyor!'
        
        # Flask'ı thread'de çalıştır
        from threading import Thread
        thread = Thread(target=lambda: app.run(host='0.0.0.0', port=8080, debug=False))
        thread.daemon = True
        thread.start()
        logger.info("🌐 Keep-alive server başlatıldı")
        
    except Exception as e:
        logger.warning(f"Keep-alive başlatılamadı: {e}")

# ==================== ANA PROGRAM ====================
def main():
    """Ana bot fonksiyonu"""
    logger.info("=" * 50)
    logger.info("🤖 BOT BAŞLATILIYOR...")
    logger.info("=" * 50)
    
    # Token kontrolü
    if not TOKEN:
        logger.error("❌ TELEGRAM_TOKEN bulunamadı!")
        logger.info("ℹ️ Replit Secrets'a TELEGRAM_TOKEN ekleyin")
        return
    
    if not CHANNEL:
        logger.error("❌ TELEGRAM_CHANNEL bulunamadı!")
        return
    
    logger.info(f"🔑 Token: {'*' * 20}{TOKEN[-5:]}")
    logger.info(f"📢 Kanal: {CHANNEL}")
    
    # Türkiye saati
    tr_timezone = pytz.timezone('Europe/Istanbul')
    tr_time = datetime.now(tr_timezone).strftime('%d.%m.%Y %H:%M:%S')
    logger.info(f"🕐 Türkiye Saati: {tr_time}")
    logger.info("")
    
    # Bot izinlerini kontrol et
    if not check_bot_permissions():
        logger.error("❌ Bot izinleri yetersiz! İşlem durduruldu.")
        return
    
    # Zamanlamaları ayarla
    schedules = setup_schedules()
    
    # Keep-alive başlat (Replit için)
    keep_alive()
    
    logger.info("✅ Zamanlayıcı başlatıldı, mesajlar bekleniyor...")
    logger.info("=" * 50)
    
    # Ana döngü
    try:
        while True:
            schedules.run_pending()
            time.sleep(60)  # 1 dakika bekle
            
            # Her saat başı durum logu
            if datetime.now().minute == 0:
                logger.info(f"⏰ Sistem çalışıyor: {datetime.now().strftime('%H:%M')}")
                
    except KeyboardInterrupt:
        logger.info("👋 Bot durduruluyor...")
    except Exception as e:
        logger.error(f"❌ Beklenmeyen hata: {e}")

# ==================== BAŞLATMA ====================
if __name__ == '__main__':
    main()